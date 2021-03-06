#!/usr/bin/env python
import lcatr.schema
import siteUtils
import metUtils
from MetrologyData import md_factory

producer = 'SR-RSA-MET-07'
testtype = 'FLATNESS'
results = []
#results = metUtils.aggregate_filerefs(producer, testtype)

#sensorData = md_factory.load('flatness.pickle')
#results.append(lcatr.schema.valid(lcatr.schema.get('flatness'),
#                                  residual_025=sensorData.quantiles['0.025'],
#                                  residual_975=sensorData.quantiles['0.975']))

results.append(siteUtils.packageVersions())

lcatr.schema.write_file(results)
lcatr.schema.validate_file()
