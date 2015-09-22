#!/usr/bin/env python
import os
import sys
import lsst.eotest.sensor as sensorTest
import siteUtils
import eotestUtils

sensor_id = siteUtils.getUnitId()
lambda_files = siteUtils.dependency_glob('*_lambda_flat_*.fits',
                                         jobname=siteUtils.getProcessName('qe_acq'),
                                         description='Lambda files:')

pd_ratio_file = eotestUtils.getPhotodiodeRatioFile()
if pd_ratio_file is None:
    message = ("The test-stand specific photodiode ratio file is " +
               "not given in config/%s/eotest_calibrations.cfg." 
               % siteUtils.getSiteName())
    raise RuntimeError(message)

mask_files = eotestUtils.glob_mask_files()
gains = eotestUtils.getSensorGains()

task = sensorTest.QeTask()
task.run(sensor_id, lambda_files, pd_ratio_file, mask_files, gains)
