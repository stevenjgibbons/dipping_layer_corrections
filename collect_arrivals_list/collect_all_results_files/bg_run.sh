#!/bin/sh
# sh multiple_days_collect.sh earthquake_list.txt  > logfile.txt 2>&1 &
# sh multiple_days_collect_MKAR.sh datesonly.txt  > logfile.txt 2>&1 &
# sh  filter_all_isf_files.sh > logfile.txt 2>&1 &
# sh multiple_days_collect_PDYAR.sh dates_2022_05_01_to_2024_03_01.txt   > logfile.txt 2>&1 &
# sh multiple_days_collect.sh dates_2022_05_01_to_2024_03_01.txt   > logfile.txt 2>&1 &
sh  run_all.sh > logfile.txt 2>&1 &
