#!/bin/tcsh

set now = `date +%s`

foreach i (`cat plotchans.list`)
echo "generate plot data for $i"

set selection = 'select id from datadesc where name='\"$i\"';'
echo "selection=("$selection")"

set getid = 'mysql CCSTrending4 -h lsstdb2.rcf.bnl.gov -u ccs -s -r --password=vst4lsst --execute='\'"$selection"\'''
echo getid = $getid

set id = `eval $getid | tail -1`
echo id for $i is $id


#set selection = 'set @tstart=UNIX_TIMESTAMP(NOW())*1000 - 120000;select tstampmills/1000.,doubleData from rawdata where tstampmills>@tstart and descr_id='$id' order by -tstampmills;'

set tstart = `grep "start tstamp" rebalive_results.txt | cut -d ":" -f 2`
set tstop = `grep "stop tstamp" rebalive_results.txt | cut -d ":" -f 2`

#set selection = 'set @tstart='$now'*1000 - 30000;select tstampmills/1000.,doubleData from rawdata where tstampmills>@tstart and descr_id='$id' order by -tstampmills;'
set selection = 'set @tstart='$tstart'*1000;set @tstop='$tstop'*1000;select tstampmills/1000.,doubleData from rawdata where tstampmills>@tstart and tstampmills<@tstop and descr_id='$id' order by -tstampmills;'
echo "selection=($selection)"
set outfl = `echo $i | awk -F '/' '{print $2}'`
echo "title time "$i >! $outfl.dat
eval mysql CCSTrending4 -h lsstdb2.rcf.bnl.gov -u ccs -s -r --password=vst4lsst --execute=\'"$selection"\'  >> $outfl.dat


end

eval 'gnuplot < rebalive_plots.gp'
