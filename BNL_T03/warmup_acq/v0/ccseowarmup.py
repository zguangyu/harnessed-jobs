###############################################################################
# warmup_acq
# - turn off cryotiger and control the warm-up
#
###############################################################################

from org.lsst.ccs.scripting import *
from java.lang import Exception
import sys
import time
import eolib

CCS.setThrowExceptions(True);

try:
#attach CCS subsystem Devices for scripting
    print "Attaching teststand subsystems"
    tssub  = CCS.attachSubsystem("%s" % ts);
    print "attaching PDU subsystem"
    pdusub = CCS.attachSubsystem("%s/PDU" % ts );

    time.sleep(3.)

    cdir = tsCWD

# turn off power to the cryotiger
    result = pdusub.synchCommand(120,"setOutletState",cryo_outlet,False);
    rply = result.getResult();

# move to TS idle state
    print "setting acquisition state"
    result = tssub.synchCommand(60,"setTSIdle");
    rply = result.getResult();

except Exception, ex:

    raise Exception("There was an exception in the acquisition producer script. The message is\n (%s)\nPlease retry the step or contact an expert," % ex)


print "TS3_warmup: COMPLETED"