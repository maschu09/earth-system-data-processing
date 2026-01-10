This project demonstrates accessing, downloading, and analyzing ERA5 reanalysis single-level data using the Copernicus Climate Data Store (CDS) API. It includes scripts for data requests, quality-checking, visualization, and discussion of scalability for handling larger datasets.
## Dataset Used
**Name:** ERA5 Hourly Data on Single Levels
**Provider:** Copernicus Climate Data Store (CDS)
**Temporal resolution:** Hourly
**Spatial resolution:** 0.25° × 0.25°
**Coverage:** Global
**Format:**NetCDF

## Variables

- Boundary layer height
- 2m temperature
- 10m wind components
## References

- Hersbach et al. (2020). The ERA5 Global Reanalysis. QJRMS.
- Copernicus Climate Data Store: https://cds.climate.copernicus.eu
## Packages used
cdsapi,xarray,numpy,matplotlib,netcdf4
## Challenges encountered
During this project, several practical challenges arose related to discovering, accessing, downloading, and processing ERA5 boundary layer height (BLH) data from the ECMWF Copernicus Climate Data Store (CDS). These issues, along with their causes and solutions, are documented below because they provided valuable insights into working with large atmospheric datasets.

Issues with downloading failure were avoided by choosing specific coordinates to minimize the size of the download file. However,  for the same script while downloading data for 2-3 years at a time was not possible as the request was deemed as too large. To avoid this problem it would be prudent to keep the data request month by month, keeping the domains small, or minimizing the number of variables.

Files downloaded without a true time coordinate or with a differently named time axis.
**Solution:** 
```python
if "valid_time" in ds.coords:
    ds = ds.rename({"valid_time": "time"})
```
**Author:** Md. Kafioul Azam

