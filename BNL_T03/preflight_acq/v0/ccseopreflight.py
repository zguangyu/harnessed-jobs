###############################################################################
# preflight_acq
# test the test stand for readiness
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time
import eolib

CCS.setThrowExceptions(True);

doarch = True

try:
#attach CCS subsystem Devices for scripting
    print "Attaching teststand subsystems"
    tssub  = CCS.attachSubsystem("%s" % ts);
    print "attaching Bias subsystem"
    biassub = CCS.attachSubsystem("%s/Bias" % ts);
    print "attaching PD subsystem"
    pdsub   = CCS.attachSubsystem("%s/PhotoDiode" % ts);
    print "attaching Mono subsystem"
    monosub = CCS.attachSubsystem("%s/Monochromator" % ts );
    print "attaching PDU subsystem"
    pdusub = CCS.attachSubsystem("%s/PDU" % ts );
    print "Attaching archon subsystem"
    arcsub  = CCS.attachSubsystem("%s" % archon);

    time.sleep(3.)

    cdir = tsCWD

    result = tssub.synchCommand(10,"getCCSVersions");
    ccsversions = result.getResult()
    ccsvfiles = open("%s/ccsversion" % cdir,"w");
    ccsvfiles.write("%s" % ccsversions)
    ccsvfiles.close()
#    print "ccsversions = %s" % ccsversions
    ssys = ""

    ts_version = ""
    archon_version = ""
    ts_revision = ""
    archon_revision = ""
    for line in str(ccsversions).split("\t"):
        tokens = line.split()
        if (len(tokens)>2) :
            if ("ts" in tokens[2]) :
                ssys = "ts"
            if ("archon" in tokens[2]) :
                ssys = "archon"
#            print "tokens[1] = %s " % tokens[1]
            if (tokens[1] == "Version:") :
                print "%s - version = %s" % (ssys,tokens[2])
                if (ssys == "ts") :
                    ts_version = tokens[2]
                if (ssys == "archon") :
                    archon_version = tokens[2]
            if (len(tokens)>3) :
                if (tokens[2] == "Rev:") :
                    print "%s - revision = %s" % (ssys,tokens[3])
                    if (ssys == "ts") :
                        ts_revision = tokens[3]
                    if (ssys == "archon") :
                        archon_revision = tokens[3]
#                print "tokens[2] = %s " % tokens[2]
#       print "\nCCSVersions line = %s \n" % line

# Initialization

    result = pdsub.synchCommand(10,"softReset");
    buff = result.getResult()

# move TS to ready state
    result = tssub.synchCommand(60,"setTSReady");
    reply = result.getResult();
    result = tssub.synchCommand(120,"goTestStand");
    rply = result.getResult();

    print "test stand in ready state, now the controller will be configured. time = %f" % time.time()

    if (doarch) :
        print "Loading configuration file into the Archon controller"
        result = arcsub.synchCommand(20,"setConfigFromFile",acffile);
        reply = result.getResult();
        print "Applying configuration"
        result = arcsub.synchCommand(25,"applyConfig");
        reply = result.getResult();
        print "Powering on the CCD"
        result = arcsub.synchCommand(30,"powerOnCCD");
        reply = result.getResult();
        time.sleep(60.);
        arcsub.synchCommand(10,"setAcqParam","Nexpo");
        arcsub.synchCommand(10,"setParameter","Expo","1");

    print "Setting the current ranges on the Bias and PD devices"
    biassub.synchCommand(10,"setCurrentRange",0.0002)
    pdsub.synchCommand(10,"setCurrentRange",0.00002)


# get the glowing vacuum gauge off
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,False);
    rply = result.getResult();

    lo_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_LOLIM', default='1.0'))
    hi_lim = float(eolib.getCfgVal(acqcfgfile, 'LAMBDA_HILIM', default='120.0'))
    bcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_BCOUNT', default='1'))
#    imcount = int(eolib.getCfgVal(acqcfgfile, 'LAMBDA_IMCOUNT', default='1'))
    imcount = 1

    seq = 0

#number of PLCs between readings
    nplc = 1

    ccd = CCDID
    result = arcsub.synchCommand(10,"setCCDnum",ccd)
    print "Working on CCD %s" % ccd

    print "set filter position"
    monosub.synchCommand(30,"setFilter",1); # open position

# go through config file looking for 'qe' instructions
    print "Scanning config file for LAMBDA specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");

    print "Scan at a low and a high wavelength to test monochromator and filter wheel"
    for wl in [450.,823.] :

            target = float(wl)
            print "target wl = %f" % target;

            result = arcsub.synchCommand(10,"setHeader","SequenceNumber",seq)


#            exptime = eolib.expCheck(calfile, labname, target, wl, hi_lim, lo_lim, test='LAMBDA', use_nd=False)
            exptime = 1.0

## take bias images
            if (doarch) :
#                result = arcsub.synchCommand(10,"setParameter","ExpTime","0"); 
#                arcsub.synchCommand(10,"setParameter","Light","0");

                print "setting location of bias fits directory"
                arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));


# take light exposures
                arcsub.synchCommand(10,"setParameter","Light","1");
                arcsub.synchCommand(10,"setParameter","Fe55","0");
                result = arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));
                rply = result.getResult()
                print "setting location of fits exposure directory"
                arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));

# prepare to readout diodes
            nreads = exptime*60/nplc + 200
            if (nreads > 3000):
                nreads = 3000
                nplc = exptime*60/(nreads-200)
                print "Nreads limited to 3000. nplc set to %f to cover full exposure period " % nplc

            monosub.synchCommand(60,"setTimeout",300.);

            for i in range(imcount):
                print "starting acquisition step for lambda = %8.2f" % wl

                print "Setting the monochromator wavelength and filter"
#                print "You should HEAR some movement"
                result = monosub.synchCommand(120,"setWaveAndFilter",wl);
                rply = result.getResult()
                time.sleep(4.)
                try:
                    print "Verifying wavelength setting of the monochromator"
                    result = monosub.synchCommand(20,"getWave");
                    rwl = result.getResult()
                except ScriptingTimeoutException, ex:
                    print "first getWave attempt failed. Trying one more time ..."
                    time.sleep(4.)
                    result = monosub.synchCommand(20,"getWave");
                    rwl = result.getResult()

                print "publishing state"
                result = tssub.synchCommand(60,"publishState");

                result = arcsub.synchCommand(10,"setHeader","MonochromatorWavelength",rwl)
#                result = arcsub.synchCommand(10,"setHeader","MonochromatorWavelength",str(rwl))

                print "getting filter wheel setting"
                result = monosub.synchCommand(60,"getFilter");
                ifl = result.getResult()
                print "The wavelength is at %f and the filter wheel is at %f " % (rwl,ifl)
                time.sleep(4.);
                

# adjust timeout because we will be waiting for the data to become ready
                mywait = nplc/60.*nreads*1.10 ;
                print "Setting timeout to %f s" % mywait
                pdsub.synchCommand(1000,"setTimeout",mywait);

                print "Starting Photo Diode recording at %f" % time.time()
                print "You should see digits changing on the PD device"
                pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

                print "recording should now be in progress and the time is %f" % time.time()

# start acquisition
                timestamp = time.time()
                fitsfilename = "%s_preflight_%3.3d_flat_%d_${TIMESTAMP}.fits" % (ccd,int(wl),seq)
                if (doarch) :
                    arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
                    result = arcsub.synchCommand(10,"setHeader","TestType","PREFLIGHT")
                    result = arcsub.synchCommand(10,"setHeader","ImageType","FLAT")

# make sure to get some readings before the state of the shutter changes       
                time.sleep(0.2);
 
                if (doarch) :
                    print "Taking an image now. time = %f" % time.time()
                    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                    fitsfilename = result.getResult();
                else :
                    time.sleep(exptime)
                print "Done taking image at %f" % time.time()

                print "done with exposure # %d" % i
                print "retrieving photodiode readings at time = %f" % time.time();

                pdfilename = "pd-values_%d-for-seq-%d-exp-%d.txt" % (int(timestamp),seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
                print "starting the wait for an accumBuffer done status message at %f" % time.time()
                tottime = pdresult.get();

# make sure the sample of the photo diode is complete
                time.sleep(10.)

                print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdfilename)
                result = pdsub.synchCommand(1000,"readBuffer","%s/%s" % (cdir,pdfilename));
                buff = result.getResult()
                print "Finished getting readings at %f" % time.time()

# reset timeout to something reasonable for a regular command
                pdsub.synchCommand(1000,"setTimeout",10.);

                if (doarch) :
                    result = arcsub.synchCommand(200,"addBinaryTable","%s/%s" % (cdir,pdfilename),fitsfilename,"AMP0","AMP0_MEAS_TIMES","AMP0_A_CURRENT",timestamp)
#/home/ts3prod/jobHarness/jh_stage/e2v-CCD/NoCCD1/ready_acq/v0/180/pd-values_1434501729-for-seq-0-exp-1.txt /home/ts3prod/jobHarness/jh_stage/e2v-CCD/NoCCD1/ready_acq/v0/180/NoCCD1_lambda_400_000_lambda_1_20150616204212.fits MP time pd 123.00
                    fpfiles.write("%s %s/%s %f\n" % (fitsfilename,cdir,pdfilename,timestamp))

            seq = seq + 1

    fpfiles.close();
    fp.close();

    fp = open("%s/status.out" % (cdir),"w");

    istate=0;
    result = tssub.synchCommandLine(10,"getstate");
    istate=result.getResult();
    fp.write(`istate`+"\n");
    fp.write("%s\n" % ts_version);
    fp.write("%s\n" % ts_revision);
    fp.write("%s\n" % archon_version);
    fp.write("%s\n" % archon_revision);
    fp.close();

# move TS to ready state                    
    tssub.synchCommand(60,"setTSReady");

# get the glowing vacuum gauge back on
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,True);
    rply = result.getResult();

    print " =====================================================\n"
    print "            PREFLIGHT DATA ACQUISITION DONE\n"
    print "          CHECK FOR A WIDGET APPEARING THAT WILL\n"
    print "           INDICATE WHETHER THE DATA LOOKS OK\n"
    print " =====================================================\n"

except Exception, ex:

# move TS to ready state                    
    tssub.synchCommand(60,"setTSReady");

# get the glowing vacuum gauge back on
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,True);
    rply = result.getResult();
    result = pdsub.synchCommand(10,"softReset");
    raise Exception("There was an exception in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)

except ScriptingTimeoutException, ex:

# move TS to ready state                    
    tssub.synchCommand(60,"setTSReady");

# get the glowing vacuum gauge back on
    result = pdusub.synchCommand(120,"setOutletState",vac_outlet,True);
    rply = result.getResult();
    result = pdsub.synchCommand(10,"softReset");
    raise Exception("There was a ScriptingTimeoutException in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)

print "preflight_acq: COMPLETED"
