This folder contains scripts for collecting arrivals lists from the bulletin of the International Seismological Center (www.isc.ac.uk).  
The idea is that way request contributions for one station for one day at a time. This seems optimal with regards to demands on the ISC servers.  

A key script is **one_array_one_day_request.sh**  
This takes four arguments, station, year, month, day, e.g.  
```
sh ./one_array_one_day_request.sh    ASAR       2017     09      03
```
and it will then generate a directory with the name of the station, e.g. ASAR, and attempt to generate a file 
**ASAR_2017_09_03.isf**  

A script **all_arrays_one_day_request.sh** loops around multiple stations (hard coded in the script) for a single day, e.g.  
```
sh ./all_arrays_one_day_request.sh 2009     05      25
```
will collect all the specified arrays for that date.  

If you have a text file, e.g. **datesonly.txt**, with the format  
```
2001 02 04
2001 02 05
2001 02 17
```
then
```
sh ./multiple_days_collect.sh datesonly.txt
```
will collect all of the arrays for all of the dates specified.  


