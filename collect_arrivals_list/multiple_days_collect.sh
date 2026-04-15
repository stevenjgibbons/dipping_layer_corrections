#!/bin/sh
#
# Takes the name of a file in which the first
# three terms are yyyy mm dd
# integers of days we are interested in.
#
scriptname=./multiple_days_collect.sh
if [ $# != 1 ]
then
  echo
  echo "USAGE: "
  echo "sh $scriptname   inputfile "
  echo
  exit 1
fi
#
inputfile=$1
if test ! -r ${inputfile}
then
  echo "No file ${inputfile} found ... "
  exit 1
fi
while read line
do
  yy=`echo "${line}" | awk '{print $1}'`
  mm=`echo "${line}" | awk '{print $2}'`
  dd=`echo "${line}" | awk '{print $3}'`
  firstchar=`echo ${yy} | cut -c1-1`
  if [ $firstchar = "2" ]
  then
    echo "Running line: $line"
    sh ./all_arrays_one_day_request.sh ${yy}  ${mm}  ${dd} 
  else
    echo "Ignore line: $line"
  fi
done < ${inputfile}
