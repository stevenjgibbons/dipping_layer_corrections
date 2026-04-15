This folder contains scripts for collecting arrivals lists from the bulletin of the International Seismological Center (www.isc.ac.uk).  
The idea is that way request contributions for one station for one day at a time. This seems optimal with regards to demands on the ISC servers.  

A key script is **one_array_one_day_request.sh**  
This takes four arguments, station, year, month, day, e.g.  
```
sh ./one_array_one_day_request.sh    ASAR       2017     09      03
```
and it will then generate a directory with the name of the station, e.g. ASAR, and attempt to generate a file 
**ASAR_2017_09_03.isf**  


