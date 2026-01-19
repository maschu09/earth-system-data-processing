# Homework 2
Author: Johanna Kasischke
Module: Earth System Data Processing

## Part 1: Set-up of control flow
A control flow determines which part of the program, e.g. functions or statements, executes next. Some programming languages contain so called "control statements" (e.g. if/else statements). By default, a program runs line by line from top to bottom. With control structures (conditionals, loops, function calls), the default flow is altered.

### Objective
For the first part of the homework, we need to set-up a control flow that handles daily data. 
The workflow will be tested with a mock processing that doesn't download any data.

### Code implementation
The mock workflow can be executed by running the file `control_flow.py`.

At the beginning of the script the following modules are imported: `argparse`, `random`, and the `datetime, timedelta, date` subclasses from the `datetime` module.
The only parameter that must be defined initially is the start date of the project (e.g. `date(2026, 1, 1)`, which represents the beginning of the processing period.
Several mock functions are then defined to represent a realistic data-processing pipeline.
The functions are: `download_data`, `process_data`, `archive_data` and `run_pipeline` 
These functions do not perform real data operations but are used to test the logic of the workflow.

**The `main()` function**

The function `main` executes the code above in the following way:

1. The Argument Parser
With the `main()`function, the script can be runned from the command line with a specific date. The specific date can be included as a string and the lambda function converts the input string automatically into a Python date object.

There are two sencarios that are handled:
1. Call script with date argument
If a date argument is provided, the script just executes `run_pipeline()` for the specific day. 
2. No data provided
If no date is provided, the script is looking for missing data until today and runs the pipeline for every missing day. If the `run_pipeline()` function fails (randomly) for a day, the entire loop breaks. 

At the end of the script, two datasets were already added to the ARCHIVE folder to simulate a real scenario, where the code needs to look for missing data files. 

## Part 2: Download ERA5 humidity data
For the next part of the exercise, ERA5 humidity data is downloaded for the period 2024-12-01 to 2024-12-05 in 6-hourly intervals on pressure levels 975, 900, 800, 500, 300 hPa in the original lat-lon resolution.

**Dataset description**

For this task the **ERA5 hourly data on pressure levels from 1940 to present** dataset is used. 

The “ERA5 hourly data on pressure levels from 1940 to present" dataset is part of the fifth generation reanalysis provided by the ECMWF. The ERA5 dataset offers hourly estimates for a large number of atmospheric, ocean-wave and land-surface quantities from 1940 until today. This dataset is regridded to a regular lat-lon of 0.25 degrees for the reanalysis. It has a vertical coverage from 1000 hPa to 1hPa and the vertical resolution is 37 pressure levels. The temporal resolution is hourly. The data can be found in the Copernicus data store or under the following link: [https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-pressure-levels?tab=overview)

### Code structure:


1. `load_ERA5_data.py` script
Here, the following parameters can be changed:
    - variable (e.g. specific humidity)
    - pressure level
    - start and end date of the download 
    - if needed, the data_format and download_format
    
All other parameters remain fixed in the `ERA5_control_flow.py` file.

2. `ERA5_control_flow.py` script

The script contains the main function `retrieve_and_process()`, which performs the complete workflow of downloading, processing, interpolation and saving the data.
To work with the script, the following modules need to be installed:
    - `cdsapi` for downloading the ERA5 data
    - `datetime`for handling dates
    - `healpy`for interpolating the data into a healpix grid
    - `numpy` for working with arrays
    - `xarray` for working with netCDF files
    - `os`for file operations
    - `zarr` for using zarr as a storage method

#### Daily Processing Workflow

A daily loop is implemented to process one day at a time. For each day:

1. ERA5 data is requested from the CDS API for the specific day, with chosen variables, times and pressure levels
2. The current netCDF file is loaded with xarray
3. The coordinates are converted into HEALPix coordinates:
    - theta = colatitude (90° - latitude) in radians
    - phi = longitude in radians
    - `.flatten()´converts the 2D grids to 1D arrays 
4. For each HEALPix resolution, an empty HEALPix array (time × level × npix) is created and filled with `hp.UNSEEN`

#### Interpolation to HEALPix Grid
The interpolation is performed seperately for each time and pressure-level combination. 
- First it is searched for valid (non-NaN) data points. 
    - `np.bincount` with pix_indices: counts how many grid points map to each HEALPix pixel
    - `np.bincount` with weights: sums the values for each HEALPix pixel
- Then the sum is divided by count to get the average value per pixel. 
The interpolated data is reshaped back into their original dimensions and stored in an xarray DataArray.

#### Zarr Output and Chunking strategy
After interpolation, all variables are combined into a single xarray dataset and the HEALPix resolution (NSIDE) is stores as metadata.

Then the data is saved in Zarr format using the following strategy:
- Chunking
    - One day per chunk along the `time` dimension
    - All pressure levels and HEALPix pixels are stored together
- Appending
    - If file exists: append new day's data along time dimension
    - If new file: create with chunking strategy (1 day per chunk) and consolidated metadata
- Metadata    
    - Consolidated metadata allows xarray to quickly read dimensions without loading all data


#### HEALPix Coordinate Convention
The standard coordinates are the colatitude (theta),0 at the North Pole, pi/2 at the equator and pi at the South Pole and the longitude (Phi) between 0 and 2 pi eastward, in a Mollview projection,phi=0 is at the center and increases eastward toward the left of the map. When visualized using a Mollview projection (`hp.mollview`), phi = 0 is located at the center of the map and increases eastward toward the left.

## Comment on the plots
The resolution of the regridded data is not sufficient. I think, I might have an issue with the coordinates and the HealPix grid. But the computation time for creating the plots is much faster than with the original netCDF files. 


## Tools
Claude AI was used for general troubleshooting.

## References
Hersbach, H., Bell, B., Berrisford, P., Biavati, G., Horányi, A., Muñoz Sabater, J., Nicolas, J., Peubey, C., Radu, R., Rozum, I., Schepers, D., Simmons, A., Soci, C., Dee, D., Thépaut, J-N. (2023): ERA5 hourly data on pressure levels from 1940 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS), DOI: 10.24381/cds.bd0915c6 (Accessed on 11 Jan. 2026)