***ESDP Homework 1***

This repository contains a Jupyter Notebook suitable to download data form the Global satellite-based surface albedo dataset.



This repository contains the script load\_cds\_albedo.ipynb, developed to access and download large-volume Earth system data from the Copernicus Data Store (CDS). The script serves as a working example for identifying and accessing large-scale satellite datasets and using the Python cdsapi client for efficient data retrieval.



Dataset Description: Global Surface Albedo



The data is derived from multiple missions, including NOAA AVHRR and Sentinel-3 OLCI and SLSTR sensors, and is provided by the CDS, which is part of the European Centre for Medium-Range Weather Forecasts (ECMWF) infrastructure.



Physical Variable: For this particular assignment, the primary output is the broadband hemispherical surface albedo (albb-bh), which measures the reflectivity of the Earth's surface. This variable consists of the integration of the directional albedo over the illumination hemisphere. It assumes a complete diffuse illumination. Also called white-sky albedo. The integration is computed over visible band \[0.4-0.7µm], near infrared band \[0.7-4µm] and over total spectrum \[0.4-4µm]. Other variables that could also be downloaded are broadband directional surface albedo (albb-dh), spectral directional surface albedo (albb-bh), and spectral hemispherical surface albedo (alsp-bh).



Data Structure and Format: The data is gridded at a horizontal resolution of 4km, 1km or 300m (depending on the satellite that recorded it). The temporal resolution is 10 days. The data format is NetCDF.



Temporal Scope: The script is flexible, allowing users to specify exact years, months, and nominal days for historical retrieval. However, the dataset comprehends form September 1981 to December 2024. The downloaded volume should be considered when selecting the timeframe of the to-be downloaded data (especially for the sentinel-3 data, which has higher resolution).



**Homework query**

The request was the following

* variable: albb\_bh
* satellite: noaa\_14
* sensor: avhrr
* horizontal resolution: 4 km
* product version: v2
* year: 1999
* month: 07
* nominal day: 10, 20, 31
* area: global
* format: netcdf



This resulted in a 300.73 MB netcdf file that took 1 min 42 sec to download. 





Author:
Nagibe Maroun González, Universität zu Köln, December 2025



Reference:
Copernicus Climate Change Service, Climate Data Store, (2018): Surface albedo 10-daily gridded data from 1981 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.ea87ed30 (Accessed on Dec-2025)

