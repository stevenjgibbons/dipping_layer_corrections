#!/bin/sh
scriptname=./one_array_one_day_request.sh
if [ $# != 4 ]
then
  echo
  echo "USAGE: "
  echo "sh $scriptname   station     yyyy    month   day "
  echo "sh $scriptname    ASAR       2017     09      03 "
  echo "sh $scriptname    YKA        2017     09      03 "
  echo "sh $scriptname    EKA        2017     09      03 "
  echo "sh $scriptname    WRA        2017     09      03 "
  echo "sh $scriptname    SPITS      2017     09      03 "
  echo "sh $scriptname    HFS        2017     09      03 "
  echo "sh $scriptname    NOA        2017     09      03 "
  echo "sh $scriptname    FINES      2017     09      03 "
  echo "sh $scriptname    ARCES      2017     09      03 "
  echo "sh $scriptname    GERES      2017     09      03 "
  echo "sh $scriptname    AKASG      2017     09      03 "
  echo "sh $scriptname    TXAR       2017     09      03 "
  echo "sh $scriptname    NVAR       2017     09      03 "
  echo "sh $scriptname    PDAR       2017     09      03 "
  echo "sh $scriptname    ILAR       2017     09      03 "
  echo "sh $scriptname    KURBB      2017     09      03 "
  echo "sh $scriptname    MMAI       2017     09      03 "
  echo "sh $scriptname    GEYT       2017     09      03 "
  echo "sh $scriptname    USRK       2017     09      03 "
  echo "sh $scriptname    KSRS       2017     09      03 "
  echo "sh $scriptname    MJAR       2017     09      03 "
  echo "sh $scriptname    SONM       2017     09      03 "
  echo "sh $scriptname    PETK       2017     09      03 "
  echo "sh $scriptname    ZALV       2017     09      03 "
  echo "sh $scriptname    CMAR       2017     09      03 "
  echo "sh $scriptname    BRTR       2017     09      03 "
  echo "sh $scriptname    TORD       2017     09      03 "
  echo "sh $scriptname    KVAR       2017     09      03 "
  echo "sh $scriptname    ESDC       2017     09      03 "
  echo "sh $scriptname    MKAR       2017     09      03 "
  echo "sh $scriptname    BVAR       2017     09      03 "
  echo "sh $scriptname    PDYAR      2024     02      01 "
  echo
  exit 1
fi
#
station=$1
yyyy=$2
mm=$3
dd=$4
stem=${station}_${yyyy}_${mm}_${dd}
if test ! -d ${station}
then
  mkdir ${station}
fi
outfile=${station}/${stem}.isf
if test -r ${outfile}
then
  echo "File ${outfile} already exists"
  exit 1
fi
curl -L \
  "https://www.isc.ac.uk/cgi-bin/web-db-run?iscreview=&out_format=ISF2&ttime=on&ttres=on&tdef=on&phaselist=&stnsearch=STN&sta_list=${station}&stn_ctr_lat=&stn_ctr_lon=&stn_radius=&max_stn_dist_units=deg&stn_top_lat=&stn_bot_lat=&stn_left_lon=&stn_right_lon=&stn_srn=&stn_grn=&searchshape=RECT&bot_lat=&top_lat=&left_lon=&right_lon=&ctr_lat=&ctr_lon=&radius=&max_dist_units=deg&srn=&grn=&start_year=${yyyy}&start_month=${mm}&start_day=${dd}&start_time=00%3A00%3A00&end_year=${yyyy}&end_month=${mm}&end_day=${dd}&end_time=23%3A59%3A59&min_dep=&max_dep=&min_mag=&max_mag=&req_mag_type=Any&req_mag_agcy=Any&include_links=off&request=STNARRIVALS" \
  -o ${outfile}
