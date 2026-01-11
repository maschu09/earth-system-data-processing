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


2. download ERA5 humidity data
- search for data in copernicus data store
- looking for 6-hourly humidity ERA5 data on pressure levels
- first try with this data set: https://cds.climate.copernicus.eu/datasets/derived-era5-pressure-levels-daily-statistics?tab=overview
    - where is the difference in the post-processing to this data set?: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview

- should we download data for the specific humidity or the relative humidity?

- generated corresping API request on website
'''
import cdsapi

dataset = "derived-era5-pressure-levels-daily-statistics"
request = {
    "product_type": "reanalysis",
    "variable": ["specific_humidity"],
    "year": "2024",
    "month": ["12"],
    "day": [
        "01", "02", "03",
        "04", "05"
    ],
    "pressure_level": [
        "300", "500", "800",
        "900", "975"
    ],
    "daily_statistic": "daily_mean",
    "time_zone": "utc+00:00",
    "frequency": "6_hourly"
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
'''

- created virtualenv to work with xarray and don't get any problems with other pre-installed stuff

- changed code to 
import cdsapi

c = cdsapi.Client()

dataset = "derived-era5-pressure-levels-daily-statistics"
#request = {
c.retrieve(dataset, {
    "product_type": "reanalysis",
    "variable": ["specific_humidity"],
    "year": "2024",
    "month": ["12"],
    "day": [
        "01", "02", "03",
        "04", "05"
    ],
    "pressure_level": [
        "300", "500", "800",
        "900", "975"
    ],
    "daily_statistic": "daily_mean",
    "time_zone": "utc+00:00",
    "frequency": "6_hourly",
    "grid": "5.625/5.625",
    "format": "netcdf"
}, "output")

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



The standard coordinates are the colatitude (theta),0 at the North Pole, pi/2 at the equator and pi at the South Pole and the longitude (Phi) between 0 and 2 pi eastward, in a Mollview projection,phi=0 is at the center and increases eastward toward the left of the map.

1. What “within the daily batch” means in practice
For each day:
download ERA5 day
→ open NetCDF
→ regrid to HEALPix NSIDE=8
→ regrid to HEALPix NSIDE=16
→ (later: write both to Zarr)
→ move to next day
❌ Not allowed:
download all days first
regrid everything at once later

did everything wrong -> need to start with first task!!!


02.01.2026

- research for first part of homework
found this https://dev.to/kiprotichterer/extracting-data-from-an-api-using-python-requests-4h5
https://pyquesthub.com/data-extraction-from-apis-using-python-a-step-by-step-guide


## 2nd part of exercise
To download the data, the script "load_ERA5_data.py" is important and only to use. the "real" work happens in the "controll_flow.py" script.

1. "load_ERA5_data.py" script
Here, the variable, pressure level and start and end date of the download can be changed. All other variables remain fixed in the "controll_flow.py" file.

2. "controll_flow.py" script
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

