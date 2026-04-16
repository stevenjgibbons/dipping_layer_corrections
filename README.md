# dipping_layer_corrections  

A set of tools to calculate the parameters defining dipping layers beneath seismic arrays that make it necessary to apply slowness corrections.
Scripts for the whole process, from collecting bulletins from the International Seismological Center, to calculating the predicted slowness vectors, to scanning the wave speed/strike/dip parameter space, to validating the outcomes against published results.  

[![SQAaaS badge](https://github.com/EOSC-synergy/SQAaaS/raw/master/badges/badges_150x116/badge_software_bronze.png)](https://api.eu.badgr.io/public/assertions/DQUGjlnTQKuAOYP3QfxjFQ "SQAaaS bronze badge achieved")  

[![SQAaaS badge shields.io](https://img.shields.io/badge/sqaaas%20software-bronze-e6ae77)](https://api.eu.badgr.io/public/assertions/DQUGjlnTQKuAOYP3QfxjFQ "SQAaaS bronze badge achieved")  

https://sqaaas.eosc-synergy.eu/full-assessment/report/https://raw.githubusercontent.com/eosc-synergy/dipping_layer_corrections.assess.sqaaas/main/.report/assessment_output.json  

Version v1.0.0 of this repo is permanently archived on Zenodo under https://doi.org/10.5281/zenodo.19604184  

[![DOI](https://zenodo.org/badge/1211477721.svg)](https://doi.org/10.5281/zenodo.19604184)

This is mostly a collection of bash scripts and python programs.  
Copilot has been used extensively in writing the python routines.  

The programs are not yet fully tested and I am sure that there will be bugs that need fixing!  

The first stage is to collect observations. We do this from the bulletin of the ISC using the scripts contained in the folder
**collect_arrivals_list**. This provides us with sets of observed sx, sy slowness values

Then we go into the folder **AK135_all_results_files** to calculate the model-predicted (sx,sy) slownesses for each station and collect them into bins.  

We scan strike and dip space for different wave-speed contrasts in the folder **AK135_all_results_files/snells_law**.  

Finally, we can validate the estimates made and predict observed apparent velocity and backazimuth under different dipping layer scenarios in the folder
**AK135_all_results_files/snells_law/theo_2_observed_tests**.  

The folder **binned_sxsy_files** contains a "binned sx, sy" file for each IMS seismic array. Please note that these files were almost entirely automatically
generated through the scripts provided in this repo, and using fairly limited sets of observations from each station. These may be updated later, or the user is of course free to curate and/or construct their own files by different methods.  
