#!/bin/sh
for isffile in HILR/*.isf LZDM/*.isf
do
  sh filter_one_file.sh ${isffile}
done
