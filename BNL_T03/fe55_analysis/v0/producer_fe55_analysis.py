#!/usr/bin/env python
import os
# This is needed so that pyplot can write to .matplotlib
os.environ['MPLCONFIGDIR'] = os.curdir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import lsst.eotest.image_utils as imutils
import lsst.eotest.sensor as sensorTest
import siteUtils

siteUtils.aggregate_job_ids()
sensor_id = siteUtils.getUnitId()
fe55_files = siteUtils.dependency_glob('*_fe55_fe55_*.fits',
                                       jobname=siteUtils.getProcessName('fe55_acq'),
                                       description='Fe55 files:')

#
# Create a mean bias file from the 25 bias files generated by fe55_acq
#
bias_files = siteUtils.dependency_glob('*_fe55_bias_*.fits',
                                       jobname=siteUtils.getProcessName('fe55_acq'),
                                       description='Bias files:')
nf = len(bias_files)
outfile = '%(sensor_id)s_mean_bias_%(nf)i.fits' % locals()
imutils.fits_mean_file(bias_files, outfile)

#
# Create a png zoom of the upper right corner of segment 1 for an Fe55
# exposure for inclusion in the test report
#
sensorTest.fe55_zoom(fe55_files[0], size=250, amp=1)
plt.savefig('%(sensor_id)s_fe55_zoom.png' % locals())

# Roll-off defects mask needs an input file to get the vendor
# geometry, and will be used for all analyses.
rolloff_mask_file = '%s_rolloff_defects_mask.fits' % sensor_id
sensorTest.rolloff_mask(fe55_files[0], rolloff_mask_file)

task = sensorTest.Fe55Task()
task.run(sensor_id, fe55_files, (rolloff_mask_file,), accuracy_req=0.01)
