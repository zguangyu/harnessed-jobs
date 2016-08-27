#!/usr/bin/env python
from ccsTools import ccsValidator
import os
import siteUtils
import shutil
import lcatr.schema
import glob

jobDir = siteUtils.getJobDir()

shutil.copy("%s/rebalive_plots.gp" % jobDir ,os.getcwd())
shutil.copy("%s/rebalive_plots.sh" % jobDir ,os.getcwd())
shutil.copy("%s/plotchans.list" % jobDir ,os.getcwd())

os.system("./rebalive_plots.sh")

jobName = "rebalive_exposure"

results = []

alivefiles = glob.glob("*.txt")
alivefiles = alivefiles + glob.glob("*summary*")
alivefiles = alivefiles + glob.glob("*png")
alivefiles = alivefiles + glob.glob("*log*")
alivefiles = alivefiles + glob.glob("*fits")

data_products = [lcatr.schema.fileref.make(item) for item in alivefiles]
results.extend(data_products)

statusAssignments = {}

schemaFile = open("%s/%s_runtime.schema"%(jobDir,jobName),"w")
schemaFile.write("# -*- python -*-\n")
schemaFile.write("{\n")
schemaFile.write("    \'schema_name\' : \'%s_runtime\',\n"%jobName)
schemaFile.write("    \'schema_version\' : 0,\n")

statusFile = open("rebalive_results.txt")
for line in statusFile:
    print "line = %s" % line
    values = line.split("|")
    statusAssignments[values[0]] = values[1].strip("[|]").strip(",")
    schemaFile.write("    \'%s\' : str,\n"%values[0])
schemaFile.write("}\n")
schemaFile.close()

print "statusAssignments = %s" % statusAssignments

print "jobName = %s" % jobName
lcatr.schema.load("%s/%s_runtime.schema"%(jobDir,jobName))
print "schema = %s" % str(lcatr.schema.get("%s_runtime"%jobName))

#results.append(lcatr.schema.valid(lcatr.schema.get(jobName),
#                                      **statusAssignments))
results.append(lcatr.schema.valid(lcatr.schema.get("%s_runtime"%jobName),
                                      **statusAssignments))

results.append(siteUtils.packageVersions())

lcatr.schema.write_file(results)
lcatr.schema.validate_file()

fitsfiles = glob.glob("*fits")

#for fl in fitsfiles:
#    os.system("screen -d -m ds9 -scale datasec yes -scale histequ -mosaicimage iraf %s &" % fl)


#ccsValidator('rebalive_exposure')
