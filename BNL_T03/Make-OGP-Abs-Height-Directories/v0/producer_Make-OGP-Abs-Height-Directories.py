#!/usr/bin/env python
import os
import sys
import subprocess
import Tkinter
import tkMessageBox
import time


ccd = os.environ["LCATR_UNIT_ID"]
#/cygdrive/c/Production DATA/ITL-STA3800B-160641/Flatness/150812
topccddir = "/cygdrive/c/Production_DATA/%s" % ccd
print "Creating the top level directory for the CCD at %s" % topccddir

abshghtdir = "%s/AbshghtScan/" % topccddir
print "Creating directory for abshght scan results. Location is %s" % abshghtdir

abshghtdatedir = "%s%s" % (abshghtdir,time.strftime("%Y%m%d-%H:%M:%S"))
print "Creating dated abshght directory for the CCD at %s" % abshghtdatedir
os.makedirs(abshghtdatedir)

print "Please setup the OGP MeasureMind application to store results in respective abshght directory indicated above"

# leave a link to the location where the files should go
print "Making links to the data directories in %s" % os.getcwd()
os.system("ln -s %s abshghtlink" % abshghtdatedir);

os.system("ls -lrt")

#top = Tkinter.Tk()
#M = Tkinter.Button(top, text ="Please setup the OGP MeasureMind application to store<br>abshght scan results in %s abshghtdatedir<br>and<br>flatness results in %s" % (abshghtdatedir,flatdatedir), bg = "green")
#M=Tkinter.Button(top,text="test")
#M.pack()
#top.title('OGP Dirs Ready')
#top.mainloop()

print "Please setup the OGP MeasureMind application to store\nabshght scan results in %s " % (abshghtdatedir)
print "============================================="
print "Now installing scripts"
tag = os.environ["OGP_SCRIPTS_TAG"]
ogpscriptshome = os.environ["OGP_SCRIPTS_HOME"]


print "The release of OGP-scripts with tag %s will be installed" % tag
cwd = os.getcwd() 
print "copying old installation of OGP scripts to a safe place"
os.system("cd %s ; cp -Lrvp OGP-scripts old-OGP-scripts-`date +%%F-%%R`" % ogpscriptshome)
print "moving the original to /tmp"
os.system("cd %s ; cp -Lvrp OGP-scripts /tmp/ ; mv OGP-scripts moved-OGP-scripts" % ogpscriptshome)
print "downloading tar of new tag"
os.system("cd %s ; wget https://github.com/lsst-camera-dh/OGP-scripts/archive/%s.tar.gz" % (ogpscriptshome,tag))
print "untarring"
os.system("cd %s ; tar -vzxf %s.tar.gz" % (ogpscriptshome,tag))
print "making a link to it"
os.system("cd %s ; ln -s OGP-scripts-%s OGP-scripts" % (ogpscriptshome,tag))

os.system("cd %s" % cwd)

print "The OGP acquisition and analysis scripts have been installed."
