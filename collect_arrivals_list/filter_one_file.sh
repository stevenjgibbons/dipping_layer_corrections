#!/bin/sh
scriptname=./filter_one_file.sh
if [ $# != 1 ]
then
  echo
  echo "USAGE: "
  echo "sh $scriptname   isffile "
  echo "sh $scriptname   HFS/HFS_2017_09_08.isf "
  echo
  exit 1
fi
#
isffile=$1
if test ! -r ${isffile}
then
  echo "No file ${isffile} found "
  exit 1
fi
dir=`dirname ${isffile}`
stem=`basename ${isffile} .isf`
outfile=${dir}/${stem}_filt.txt
if test -r ${outfile}
then
  echo "File ${outfile} already found ..."
  echo "But continue anyway"
fi
isf_file_filter < ${isffile} > ${outfile}
python  isf_event_compute.py ${outfile}
