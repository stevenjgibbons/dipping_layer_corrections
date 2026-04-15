#!/bin/sh
for binnedfile in ../*_binned_sxsy.txt
do
  if test -r ${binnedfile}
  then 
     station=`basename ${binnedfile} _binned_sxsy.txt`
     oldstem=${station}_strike_dip_fit
     if test -r ${oldstem}.txt
     then
       mv ${oldstem}.txt ${oldstem}_orig.txt
     fi
     if test -r ${oldstem}.png
     then
       mv ${oldstem}.png ${oldstem}_orig.png
     fi
     if test -r ${oldstem}.pdf
     then
       mv ${oldstem}.pdf ${oldstem}_orig.pdf
     fi
     echo  ${binnedfile} ${oldstem}
     while read line
     do
       set $line
       alpha1=$1
       alpha2=$2
       # python sa_analyze_binned_file.py \
       python sa_analyze_binned_file_elementwise.py \
           --file  ${binnedfile}    \
           --alpha1  ${alpha1} \
           --alpha2  ${alpha2} \
           --numstrike 72 \
           --maxdip 70 \
           --numdip 30
       if test -r ${oldstem}.txt
       then
         mv ${oldstem}.txt outputs/${station}_${alpha1}_${alpha2}_StrikeDipFit.txt
       fi
       if test -r ${oldstem}.png
       then
         mv ${oldstem}.png outputs/${station}_${alpha1}_${alpha2}_StrikeDipFit.png
       fi
       if test -r ${oldstem}.pdf
       then
         mv ${oldstem}.pdf outputs/${station}_${alpha1}_${alpha2}_StrikeDipFit.pdf
       fi
     done < alpha1_alpha2.txt
  fi
done
