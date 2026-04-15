#!/bin/sh
for binnedfile in ../SPITS*_binned_sxsy.txt
do
  if test -r ${binnedfile}
  then 
     echo  ${binnedfile}
     # python sa_analyze_binned_file.py \
     python sa_analyze_binned_file_elementwise.py \
         --file  ${binnedfile}    \
         --alpha1 1.39 \
         --alpha2 1.80 \
         --numstrike 36 \
         --maxdip 70 \
         --numdip 15
  fi
done
