#!/usr/bin/env python
import siteUtils
import metUtils
from flatnessTask import flatnessTask

sensor_id = siteUtils.getUnitId()

# Find the metrology scan data
met_file = siteUtils.dependency_glob('*.dat',jobname=siteUtils.getProcessName('Pump_and_Room_Temp_Measurement'),description='')

met_file = met_file[0]  # siteUtils returns met_file as a list with one member;
                        # here take the first (and only) member

# The dtype below indicates the source of the data, which is always OGP
# for sensors measured at BNL
#flatnessTask(sensor_id, met_file, dtype='ETU', pickle_file='flatness.pickle')
