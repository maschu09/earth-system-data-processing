# Homework 2
Author: Johanna Kasischke
Module: Earth System Data Processing

## Part 1: Set-up of control flow
A control flow determines which part of the program, e.g. functions or statements, executes next. Some programming languages contain so called "control statements" (e.g. if/else statements). By default, a program runs line by line from top to bottom. With control structures (conditionals, loops, function calls), the default flow is altered.

### Objective
For the first part of the homework, we need to set-up a control flow that handles daily data. 
The workflow will be tested with a mock processing that doesn't download any data.

### Code implementation
The mock testing can be done whith executing the file `control_flow.py`.

First of all, the following modules are imported: `argparse`, `random`, and the `datetime, timedelta, date` subclasses from the `datetime`class.

The only thing that need to be defined in the first place is the start date (`date(2026, 1, 1)`) of the project or the dowloading period, respectively. Then some mock functions are created to design a workflow. The functions `download_data`, `process_data`, `archive_data` and `run_pipeline` are representative of a real download routine. 
The function `main` executes the code above in the following way:
1. The Argument Parser
With the `main()`function, the script can be runned from the command line with a specific date. The specific date can be included as a string and the lambda function converts the input string automatically into a Python date object.

There are two sencarios that need to be covered:
1. Call script with date argument
If a date argument is provided, the script just executes `run_pipeline()` for the specific day. 
2. No data provided
If no date is provided, the script is looking for missing data until today and runs the pipeline for every missing day. If the `run_pipeline()`function fails (randomly) for a day, the entire loop breaks. 

At the end of the script, two datasets were already added to the ARCHIVE folder to simulate a real scenario, where the code needs to look for missing data files. 

## Part 2: Download ERA5 humidity data
For the next part of the exercise, ERA5 humidity data should be downloaded from 2024-12-01 to 2024-12-05 in 6-hourly intervals on pressure levels 975, 900, 800, 500, 300 hPa in the original lat-lon resolution.

For this task the **ERA5 hourly data on pressure levels from 1940 to present** dataset is used. 

### The Dataset: ERA5 hourly data on pressure levels from 1940 to present

??????????????????????????

### The Code:
To download the data, the script "load_ERA5_data.py" is important and only to use. the "real" work happens in the "controll_flow.py" script.

1. "load_ERA5_data.py" script
Here, the variable, pressure level and start and end date of the download can be changed. All other variables remain fixed in the "controll_flow.py" file.

2. "ERA5_control_flow.py" script
This file contains two functions. The first function *retrieve_data* is used to retrieve the data from the API. The function is called by the second function *process_data*. 

function *retrieve_data*
needs the following arguments:
    - dataset: dataset name from the copernicus store
    - filename: name for the downloaded files. Get's changed during the loop. Single filename for every process day. 
    - request: dictionary in which the download parameters are defined. The parameters are getting defined in the "load_ERA5_data.py" file.

function *process_data*
needs the following arguments:
    - dataset: same as in the function before
    - start: start date for download
    - end: end date for download
    - variable: download variable
    - time: download specific times
    - pressure_level: pressure levels to download
    NOT NECESSARY:
    - data_format: default="netCDF", can be changed but is not needed
    - download_format: default="unarchived", can be changed to "zip"    

The while-loop loops over every day and saves every day in a single netCDF file.


## Part 3: Interpolate data to healpix grid
In the next part of the exercise, the data should be converged into a healpix grid with two resolutions: NSIDE=8 and NSIDE=16. This process shall be done in the daily batch (DO NOT first download all data and then process all data).

The routine should look as follows:
For each day:
download ERA5 day
→ open NetCDF
→ regrid to HEALPix NSIDE=8
→ regrid to HEALPix NSIDE=16
→ (later: write both to Zarr)
→ move to next day


The standard coordinates are the colatitude (theta),0 at the North Pole, pi/2 at the equator and pi at the South Pole and the longitude (Phi) between 0 and 2 pi eastward, in a Mollview projection,phi=0 is at the center and increases eastward toward the left of the map.






- installed every dependency from this website for xarray: https://docs.xarray.dev/en/stable/getting-started-guide/installing.html

### To Do next: 
- interpolate data to a healpix grid etc.
- write README consistently
- test flexibility of code --> no hardcoding

**30.12.2025**

- created conda environment on macbook to be able to work there as well
- flexible download routine

- research healpix grid https://healpix.sourceforge.io/
- installed healpy via pip
- 







02.01.2026

- research for first part of homework
found this https://dev.to/kiprotichterer/extracting-data-from-an-api-using-python-requests-4h5
https://pyquesthub.com/data-extraction-from-apis-using-python-a-step-by-step-guide



## References
Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2023): ERA5 hourly data on pressure levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.bd0915c6 (Accessed on 11 Jan. 2026)