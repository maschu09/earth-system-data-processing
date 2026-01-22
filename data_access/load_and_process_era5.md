# Homework 2
Student: Florian Bremm <br>
MatNr.: 7440728

## General Information

The contribution of this fork is the `load_and_process_era5.ipynb` as well as `load_and_process_era5.py`. The notebook and the script do the same thing, however the notebook was designed to develop basic processes while the script is more focussed on being user-friendly and robust. Due to that it's recommended to use the script for any further work and the rest of this README will focus on the script.
In its current state, this script allows the download of specific humidity [kg / kg] on the pressure levels 975hPa 900hPa 800hPa 500hPa 300hPa. This data is then transformed into a healpix grid (NSIDE-8 and NSIDE-16) and stored to a zarr archive in daily chunks. This allows fast access, downloading and storing a large amount of data with limited resources and possible distribution of the system. All essential parameters are configured centrally so repurposing of this script is possible. For example downloading different variables or storing a higher resolution healpix grid would be possible without changing functional code.

## Data Access
To access the data, authentication is required. Visit https://cds.climate.copernicus.eu/ for registration. You need to activate 
"CC-BY licence", "ERA-Interim Product licence" as well as "Data protection and privacy statement" and "Terms of use of the Copernicus Climate Data Store" under https://cds.climate.copernicus.eu/profile?tab=licences. After that you need to visit https://cds.climate.copernicus.eu/profile?tab=profile and create a `.cdsapirc` file with the provided `url` and `api-key` in your local home directory (tested on a Linux based OS). More information on the registration can be found on https://cds.climate.copernicus.eu/how-to-api

## Requirements
Successful execution of the script requires additional packages. Namely, those are cdsapi
`xarray , numpy, scipy, zarr, netcdf4, h5netcdf, healpy, matplotlib, cartopy, ipython`. By running `conda env create -f environment_era5_healpix.yml`,
`conda activate era5-healpix` all necessary packages can be installed

## Ussage Instructions 
To execute this script run ` python load_and_process_era5.py [date]` the parameter `date` decides what date range will be downloaded. Choose `assignment` for the date range specified in the assignment description. You can specify one date (format: `YYYY-mm-dd`) to download one day or a range (format: `[start]--[end]`) if you leave out start or end (for example `2026-01-01--`) the minimal date (1940-01-01) will be chosen as the start and the maximal date (today) will be chosen as the end date. If nothing is specified, the script will start downloading the entire date range.


*Author:* Florian Bremm, Department of Computer Science and Math, University of Cologne December 2025