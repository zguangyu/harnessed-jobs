###############################################################################
#
#   - Homer
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time
import eolib

CCS.setThrowExceptions(True);

cdir = tsCWD


rebsub = {}
serial_number = {}
tssub  = CCS.attachSubsystem("ts");
monosub = CCS.attachSubsystem("%s/Monochromator" % ts );
ts8sub  = CCS.attachSubsystem("%s" % ts8);
cryosub  = CCS.attachSubsystem("ts/Cryo");
pwrsub  = CCS.attachSubsystem("ccs-rebps");
pwrmainsub  = CCS.attachSubsystem("ccs-rebps/MainCtrl");
rebdevs = ts8sub.synchCommand(10,"getREBDevices").getResult()

istate = tssub.synchCommand(10,"getstate").getResult()
print "istate before = ",istate," : "
istate = (istate & 0xffffff) | (int(jobname.split("__")[1]) << 24)
print "istate after = ",istate
tssub.synchCommand(10,"setstate",istate)

if (True) :

    cdir = tsCWD

    ts_version = "NA"
    ts8_version = "NA"
    ts_revision = "NA"
    ts8_revision = "NA"

    status_value = None


    rebs = ""
    pstep = 1
    istep = 1
    try:
        result = ts8sub.synchCommand(10,"getREBDevices");
        rebs = result.getResult();
        status_value = rebs
    except:
        status_value = "failed"


    ccdnames = {}
    ccdmanunames = {}
    try:
        ccdnames["00"] = CCDS00
        ccdmanunames["00"] = CCDMANUS00
        ccdnames["01"] = CCDS01
        ccdmanunames["01"] = CCDMANUS01
        ccdnames["02"] = CCDS02
        ccdmanunames["02"] = CCDMANUS02
    except:
        pass
    try:
        ccdnames["10"] = CCDS10
        ccdmanunames["10"] = CCDMANUS10
        ccdnames["11"] = CCDS11
        ccdmanunames["11"] = CCDMANUS11
        ccdnames["12"] = CCDS12
        ccdmanunames["12"] = CCDMANUS12
    except:
        pass
    try:
        ccdnames["20"] = CCDS20
        ccdmanunames["20"] = CCDMANUS20
        ccdnames["21"] = CCDS21
        ccdmanunames["21"] = CCDMANUS21
        ccdnames["22"] = CCDS22
        ccdmanunames["22"] = CCDMANUS22
    except:
        pass

    rafttype = "E2V"
    raft = UNITID



    eolib.EOTS8Setup(tssub,ts8sub,pwrsub,raft,rafttype,cdir,sequence_file,vac_outlet)

    ts8sub.synchCommand(10,"setDefaultImageDirectory","%s" % (cdir));

    tstart = time.time()

    seqcmnd = "setSequencerStart Clear"
    print ts8sub.synchCommand(10,seqcmnd).getResult();
    while ((time.time()-tstart) < 3600.0) :
        seqcmnd = "startSequencer"
        print "seqcmnd = (%s)" % seqcmnd
        print ts8sub.synchCommand(10,seqcmnd).getResult();
        time.sleep(1.0)

    time.sleep(2.0)
    ts8sub.synchCommand(10,"setTestType TS8")
    ts8sub.synchCommand(10,"setImageType BIAS")
    rply = ts8sub.synchCommand(100,"exposeAcquireAndSave",0,False,False,"${sensorLoc}_final_image.fits").getResult()



fp = open("%s/status.out" % (cdir),"w");
fp.write(`istate`+"\n");
fp.close();


print "COMPLETED"
