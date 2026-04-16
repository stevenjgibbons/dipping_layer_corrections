
This folder contains all the "binned sx,sy" files calculated using other scripts in this repo.  
There is one file per array. Each file looks like this:  

```
  -0.02940   -0.06971    0.01877    0.03627      3
  -0.02282   -0.06773    0.04581    0.06013      1
  -0.02085   -0.06791    0.01576    0.04502      9
  -0.01528   -0.06971    0.02338    0.03845      1
  -0.01176   -0.06963    0.01127    0.04733      6
  -0.00870   -0.06982    0.02311    0.04478     33
  -0.00564   -0.06968    0.02735    0.05217     13
  -0.00051   -0.06992    0.00129    0.01795      1
   0.00206   -0.06926    0.01961    0.08229      3
```
which give 
```
median_theoretical_sx  median_theoretical_sy  median_measured_sx  median_measured_sy  number_of_elements_in_bin
```

The creation of these files was highly automated and using quite limited and randomly selected subsets of the output
for the different stations. A revision of this dataset could include a far more carefully curated set of arrivals and
a far more thorough screening of poor quality estimates.  

Indeed, we could check the sensitivity of the outcome by selecting subsets of each file.  
Do we get different results if we consider e.g. only regional or only teleseismic, regional P and regional S or
just regional P etc.?
