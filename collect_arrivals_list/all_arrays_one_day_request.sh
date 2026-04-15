#!/bin/sh
scriptname=./all_arrays_one_day_request.sh
if [ $# != 3 ]
then
  echo
  echo "USAGE: "
  echo "sh $scriptname   yyyy    month   day "
  echo "sh $scriptname   2016     09      09 "
  echo "sh $scriptname   2016     01      06 "
  echo "sh $scriptname   2013     02      12 "
  echo "sh $scriptname   2009     05      25 "
  echo "sh $scriptname   2006     10      09 "
  echo
  exit 1
fi
#
yyyy=$1
mm=$2
dd=$3
for station in \
  AKASG ARCES ASAR BRTR BVAR CMAR EKA ESDC FINES \
  GERES GEYT HFS ILAR KSRS KURBB KVAR MJAR MKAR MMAI \
  NOA NVAR PDAR PETK SONM SPITS TORD TXAR USRK WRA \
  YKA ZALV
do
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
done
