###############################################################################
# monochromator calibration script
# Acquire qe images
#
###############################################################################

from org.lsst.ccs.scripting import *
from org.lsst.ccs.messaging import CommandRejectedException
from java.lang import Exception
import sys
import time
import eolib

CCS.setThrowExceptions(True);

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

    usepdu = False

    if (usepdu) :
        print "attaching PDU subsystem"
        pdusub = CCS.attachSubsystem("%s/PDU" % ts );


    usearchon = False

    if (usearchon) :
        print "Attaching archon subsystem"
        arcsub  = CCS.attachSubsystem("%s" % archon);

    time.sleep(3.)

    cdir = tsCWD

# set the scan range here:
    wlbegin = 300.
    wlend   = 1100.

    wlstep = 10.
    result = tssub.synchCommand(120,"setDoTestStandReadyCheck",False)

# get the glowing vacuum gauge back off
    if (usepdu) :
        result = pdusub.synchCommand(120,"setOutletState",vac_outlet,False);
        rply = result.getResult();

# Initialization
    print "doing initialization"

    if (usearchon) :
        print "Loading configuration file into the Archon controller"
        result = arcsub.synchCommand(20,"setConfigFromFile",acffile);
        reply = result.getResult();
        print "Applying configuration"
        result = arcsub.synchCommand(25,"applyConfig");
        reply = result.getResult();
        print "Powering on the CCD"
        result = arcsub.synchCommand(30,"powerOnCCD");
        reply = result.getResult();
        time.sleep(3.);

        print "past powering on the CCD"

#    print "Throwing away the first image"
#    arcsub.synchCommand(10,"setFitsFilename","");
#    result = arcsub.synchCommand(200,"exposeAcquireAndSave");
#    reply = result.getResult();


        arcsub.synchCommand(10,"setAcqParam","Expo");
        arcsub.synchCommand(10,"setParameter","Nexpo","1");

        print "set expo to 1"

        for i in range(2):
            timestamp = time.time()
            result = arcsub.synchCommand(10,"setFitsFilename","");
            print "Ready to take clearing bias image. time = %f" % time.time()
            result = arcsub.synchCommand(20,"exposeAcquireAndSave");
            rply = result.getResult()
            result = arcsub.synchCommand(500,"waitForExpoEnd");
            rply = result.getResult();
        time.sleep(2.0);

    biassub.synchCommand(10,"setCurrentRange",0.00000002)
#    pdsub.synchCommand(10,"setCurrentRange",  0.0000002)
# the following was only used for the 980 nm line
    pdsub.synchCommand(10,"setCurrentRange", 0.0000002)

    print "set current ranges"

# move to TS acquisition state
    print "setting acquisition state"

    seq = 0

#number of PLCs between readings
    nplc = 1

    ccd = CCDID
    print "Working on CCD %s" % ccd

    monosub.synchCommand(60,"setTimeout",300.);

#    print "set filter position"
#    result = monosub.synchCommand(60,"setFilter",3);
    rply = result.getResult()
    result = monosub.synchCommand(60,"setSlitSize",1,2000);
    rply = result.getResult()
    result = monosub.synchCommand(60,"setSlitSize",2,2000);
    rply = result.getResult()

# go through config file looking for 'qe' instructions
    print "Scanning config file for LAMBDA specifications";
    fp = open(acqcfgfile,"r");
    fpfiles = open("%s/acqfilelist" % cdir,"w");

# take light exposures
    if (usearchon) :
        arcsub.synchCommand(10,"setParameter","Light","1");
        print "setting location of fits exposure directory"
        arcsub.synchCommand(10,"setFitsDirectory","%s" % (cdir));


#def my_range(start, end, step):
#    while start <= end:
#        yield start
#        start += step
#
#for x in my_range(1, 10, 0.5):
#    print x

# -------------------------------------
    wl=wlbegin - wlstep
    nwl = int((wlend - wlbegin) / wlstep + 1)
    for idx in range(nwl):
        wl = wl + wlstep
#    for wl in [473.4, 473.4, 881.9, 881.9] :
#    for wl in range(440.,441.,0.3):



        exptime = 25.
        nreads = 3000
        if (usearchon) :
            arcsub.synchCommand(10,"setParameter","ExpTime",str(int(exptime*1000)));

# adjust timeout because we will be waiting for the data to become ready
        mywait = nplc/60.*nreads*2.0 ;
        print "Setting timeout to %f s" % mywait

        result = monosub.synchCommand(900,"setWaveAndFilter",wl);
        rwl = result.getResult()
        print "The wl retrieved from the monochromator is rwl = %f" % rwl

        if (usearchon) :
            result = arcsub.synchCommand(10,"setHeader","MonochromatorWavelength",rwl)

        print "the wavelength read back is %f for seq %d" % (rwl,seq)
        print "publishing state"
        result = tssub.synchCommand(120,"getstate");
        stt = result.getResult()
        result = tssub.synchCommand(120,"setstate",stt);

        for i in range(1):
            print "starting acquisition step for lambda = %8.2f" % wl
# PD from PD setup
            print "Setup regular PD readout"
            pdsub.synchCommand(1000,"setTimeout",mywait);

            print "call accumBuffer to start PD recording at %f" % time.time()
            pdresult =  pdsub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

            print "PD recording from PD device should now be in progress and the time is %f" % time.time()

# PD from BIAS setup
            print "Setup PD readout from Bias device"
            biassub.synchCommand(1000,"setTimeout",mywait);

            print "call accumBuffer to start PD recording from Bias device at %f" % time.time()
            pdbiasresult =  biassub.asynchCommand("accumBuffer",int(nreads),float(nplc),True);

            print "PD recording from Bias device should now be in progress and the time is %f" % time.time()

            time.sleep(10.)

# start acquisition
            timestamp = time.time()
            fitsfilename = "%s_lambda_%4.4d_%3.3d_lambda_%d_${TIMESTAMP}.fits" % ("mono_calib",int(wl*10.),seq,i+1)
            if (usearchon) :
                arcsub.synchCommand(10,"setFitsFilename",fitsfilename);
                result = arcsub.synchCommand(10,"setHeader","TestType","MonoCalib")
            else :
                result = monosub.synchCommand(900,"openShutter");
                rwl = result.getResult()
                time.sleep(exptime)
                result = monosub.synchCommand(900,"closeShutter");
                rwl = result.getResult()

# make sure to get some readings before the state of the shutter changes       
            time.sleep(0.2);
 
            if (usearchon) :
                print "Ready to take image. time = %f" % time.time()
                result = arcsub.synchCommand(200,"exposeAcquireAndSave");
                fitsfilename = result.getResult();
                print "after click click at %f" % time.time()

                print "done with exposure # %d" % i

# readings from PD device
            print "getting photodiode readings from PD device at time = %f" % time.time();

            pdfilename = "pd-values_%d-for-seq-%d-exp-%d.txt" % (int(timestamp),seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
            print "starting the wait for an accumBuffer done status message at %f" % time.time()
            tottime = pdresult.get();

# make sure the sample of the photo diode is complete
            time.sleep(10.)

            print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdfilename)
#            pdrresult = pdsub.synchCommand(1000,"readBuffer","%s/%s" % (cdir,pdfilename));
            pdrresult = pdsub.asynchCommand("readBuffer","%s/%s" % (cdir,pdfilename));
#            buff = pdrresult.getResult()

# readings from PD device
            print "getting photodiode readings from Bias device at time = %f" % time.time();

            pdbiasfilename = "pdbias-values_%d-for-seq-%d-exp-%d.txt" % (int(timestamp),seq,i+1)
# the primary purpose of this is to guarantee that the accumBuffer method has completed
            print "starting the wait for an accumBuffer done status message at %f" % time.time()
            tottime = pdbiasresult.get();

# make sure the sample of the photo diode is complete
#            time.sleep(30.)

            print "executing readBuffer, cdir=%s , pdfilename = %s" % (cdir,pdbiasfilename)
            result = biassub.synchCommand(1000,"readBuffer","%s/%s" % (cdir,pdbiasfilename));
            buff = result.getResult()
            print "Finished getting readings at %f" % time.time()

            buff = pdrresult.get()
            print "Finished getting readings at %f" % time.time()
# reset timeout to something reasonable for a regular command
#            pdsub.synchCommand(1000,"setTimeout",10.);
#            biassub.synchCommand(1000,"setTimeout",10.);

            if (usearchon) :
                result = arcsub.synchCommand(200,"addBinaryTable","%s/%s" % (cdir,pdfilename),fitsfilename,"AMP0.MEAS_TIMES","AMP0_MEAS_TIMES","AMP0_A_CURRENT",timestamp)
                result = arcsub.synchCommand(200,"addBinaryTable","%s/%s" % (cdir,pdbiasfilename),fitsfilename,"AMP2.MEAS_TIMES","AMP2_MEAS_TIMES","AMP2_A_CURRENT",timestamp)

            fpfiles.write("%s %s/%s %s/%s %f\n" % (fitsfilename,cdir,pdfilename,cdir,pdbiasfilename,timestamp))

#            time.sleep(15.)

        seq = seq + 1

    fpfiles.close();
    fp.close();

    fp = open("%s/status.out" % (cdir),"w");

    istate=0;
    result = tssub.synchCommandLine(10,"getstate");
    istate=result.getResult();
    fp.write(`istate`+"\n");
    fp.close();

# move TS to idle state
                    
#    tssub.synchCommand(60,"setTSReady");

# get the glowing vacuum gauge back on
    if (usepdu) :
        result = pdusub.synchCommand(120,"setOutletState",vac_outlet,True);
        rply = result.getResult();
    result = tssub.synchCommand(120,"setDoTestStandReadyCheck",True)

except Exception, ex:

    raise Exception("There was an exception in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)


print "mono calib: END"
