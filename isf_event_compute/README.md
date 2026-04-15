A little python script **isf_event_compute.py** that reads in the output from the **isf_file_filter** program and makes a crude estimate
of the event location just based on the ISC distance and backazimuth. It appends useful parameters: the forward and backazimuths, apparent velocity, measured sx,sy, and
the observed minus predicted backazimuth.  

So, usage:  
```
isf_file_filter < GERES_2017_09_03.isf  > GERES_2017_09_03_filt.txt
```
Then, if you type
```
python isf_event_compute.py GERES_2017_09_03_filt.txt
```
it will compute the file **GERES_2017_09_03_filt_event.txt** containing the following:  
```
GERES   4.71 319.8 Pn       2017-09-03T02:56:11.975 137.2 14.0  7.6  613580235  995101753  48.8451   13.7016   45.3368    18.3213  136.41  319.80    7.94   0.085603  -0.092443    0.79
GERES   4.71 319.8 Sn       2017-09-03T02:57:04.683 146.7 30.5  1.5  613580235  995101754  48.8451   13.7016   45.3368    18.3213  136.41  319.80    3.64   0.150695  -0.229411   10.29
GERES  88.70  40.3 P        2017-09-03T03:34:32.425 235.4  3.5  4.0  613580237  995101785  48.8451   13.7016   -7.5227   -65.5871  257.00   40.30   31.75  -0.025927  -0.017886  -21.60
GERES  73.69 321.5 P        2017-09-03T03:41:36.625  43.2  6.0 28.7  613580239  995102006  48.8451   13.7016   40.6287   128.4944   45.88  321.50   18.52   0.036963   0.039361   -2.68
```

In this file we should see  
```
stat   distd trfaz phase    arrival_time            msbaz mslo  SNR  evID       arrID      stlat     stlon       evlatest  evlonest   bazstev azevst  appvel  sx_meas    sy_meas    baz_minus_true
GERES  75.32 343.4 P        2017-09-03T08:33:00.629  13.1  6.0  3.7  613580263  995103038  48.8451   13.7016     53.7114   168.8673   14.89  343.40   18.52   0.012238   0.052590   -1.79
```
where
```
stat              = Station name
distd             = distance in degrees from the ISC origin location
trfaz             = "true forward azimuth" from the ISC origin location to the station
phase             = phase name
arrival_time      = arrival pick used in bulletin in format yyyy-mm-ddThh:mm:ss.sss
msbaz             = measured backazimuth (from the data)
mslo              = measured slowness in seconds per degree - so divide by 111.12 for s/km
evID              = ISC event ID number
arrID             = ISC arrival ID number
stlat             = Station latitude
stlon             = Station longitude
evlatest          = Estimated event latitude (based on distd and trfaz)
evlonest          = Estimated event longitude (based on distd and trfaz)
bazstev           = Estimated backazimuth from station to event
azevst            = Estimated azimuth from event to station (This should be identical to trfaz - this is a sanity check)
appvel            = This is just the apparent velocity in km/s converted from mslo (observed)
sx                = Measured sx slowness estimated from appvel and bazstev
sy                = Measured sy slowness estimated from appvel and bazstev
baz_minus_true    = Observed Minus Predicted residual for backazimuth
```
