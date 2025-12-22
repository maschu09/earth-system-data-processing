#Homework 2
Johanna Kasischke

1. control flow

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
