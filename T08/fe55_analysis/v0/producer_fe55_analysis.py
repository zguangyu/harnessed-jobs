#!/usr/bin/env python
import os
import pylab
import lsst.eotest.image_utils as imutils
import lsst.eotest.sensor as sensorTest
import siteUtils

raft_id = siteUtils.getUnitId()

ccdnames = {}
ccdmanunames = {}
ccdnames,ccdmanunames = siteUtils.getCCDNames()

for sensor_id in ccdnames :
    fe55gz_files = siteUtils.dependency_glob('*/%s_fe55_fe55_*.fits.gz' % sensor_id slotd,
                                       jobname=siteUtils.getProcessName('fe55_acq'),
                                       description='Fe55 files:')
    for fe55gz_file in fe55gz_files:
        os.system("gunzip -v %s" % fe55gz_file)

    fe55_files = siteUtils.dependency_glob('*/%s_fe55_fe55_*.fits' % sensor_id slotd,
                                       jobname=siteUtils.getProcessName('fe55_acq'),
                                       description='Fe55 files:')
    print "fe55_files ="
    print fe55_files
    print "  =============================="
#
# Create a mean bias file from the 25 bias files generated by fe55_acq
#
    bias_files = siteUtils.dependency_glob('*/%s_fe55_bias_*.fits' % sensor_id,
                                       jobname=siteUtils.getProcessName('fe55_acq'),
                                       description='Bias files:')
    nf = len(bias_files)
#    outfile = '%(raft_id)s_mean_bias_%(nf)i.fits' % locals()
    outfile = '%s_mean_bias_%(nf)i.fits' % sensor_id
    imutils.fits_mean_file(bias_files, outfile)

#
# Create a png zoom of the upper right corner of segment 1 for an Fe55
# exposure for inclusion in the test report
#
    sensorTest.fe55_zoom(fe55_files[0], size=250, amp=1)
#pylab.savefig('%(raft_id)s_fe55_zoom.png' % locals())
    pylab.savefig('%s_fe55_zoom.png' % sensor_id)

# Roll-off defects mask needs an input file to get the vendor
# geometry, and will be used for all analyses.
#    rolloff_mask_file = '%s_rolloff_defects_mask.fits' % raft_id
    rolloff_mask_file = '%s_rolloff_defects_mask.fits' % sensor_id
    sensorTest.rolloff_mask(fe55_files[0], rolloff_mask_file)

    task = sensorTest.Fe55Task()
    task.run(raft_id, fe55_files, (rolloff_mask_file,), accuracy_req=0.01)
