# Earth System Data Processing

Collection of notebooks and information on various aspects of Earth system data processing.

This repository contains material that has been provided for and developed during the lecture on
*Earth System Data Processing* at the University of Cologne in the winter semester 2025/26. The lecture
covered topics such as finding and accessing data from modern web services, coordinate systems,
remapping and interpolation, common file formats, types of Earth system data, numerical model grids,
metadata standards, FAIR data.

The course uses an inverse classroom concept, where the actual lectures are recorded, while students
discuss the lecture content and work on practical examples during the course hours. The material 
in this repository forms the basis for the practical exercises. Students will also be assigned 
coding tasks as homework and the results shall be included here to establish a collection of useful routines 
for other students and scientists who wish to learn the basics of Earth system data processing.

*Note:* Due to the background of the lecturer, the focus of this material is on atmospheric data.
Nevertheless, many concepts and routines can also be applied to other Earth system data. Feel free to contribute
material for other data types if you find this repository useful.

*Author:* Martin Schultz, Jülich Supercomputing Centre, Forschungszentrum Jülich & Department of Computer Science and Math, University of Cologne
October 2025

# ***ESDP Homework 1***

###### Author: Nagibe Maroun González



This repository contains a Jupyter Notebook suitable to download data form the Global satellite-based surface albedo dataset.



### **Description**



This repository contains the script load\_cds\_albedo.ipynb, developed to access and download large-volume Earth system data from the Copernicus Data Store (CDS). The script serves as a working example for identifying and accessing large-scale satellite datasets and using the Python cdsapi client for efficient data retrieval.



Dataset Description: Global Surface Albedo



The data is derived from multiple missions, including NOAA AVHRR and Sentinel-3 OLCI and SLSTR sensors, and is provided by the CDS, which is part of the European Centre for Medium-Range Weather Forecasts (ECMWF) infrastructure.



Physical Variable: For this particular assignment, the primary output is the broadband hemispherical surface albedo (albb-bh), which measures the reflectivity of the Earth's surface. This variable consists of the integration of the directional albedo over the illumination hemisphere. It assumes a complete diffuse illumination. Also called white-sky albedo. The integration is computed over visible band \[0.4-0.7µm], near infrared band \[0.7-4µm] and over total spectrum \[0.4-4µm]. Other variables that could also be downloaded are broadband directional surface albedo (albb-dh), spectral directional surface albedo (albb-bh), and spectral hemispherical surface albedo (alsp-bh).



Data Structure and Format: The data is gridded at a horizontal resolution of 4km, 1km or 300m (depending on the satellite that recorded it). The temporal resolution is 10 days. The data format is NetCDF.



Temporal Scope: The script is flexible, allowing users to specify exact years, months, and nominal days for historical retrieval. However, the dataset comprehends form September 1981 to December 2024. The downloaded volume should be considered when selecting the timeframe of the to-be downloaded data (especially for the sentinel-3 data, which has higher resolution).



### **Homework query**



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



### **Challenges**

1. The first encountered issue was that the initial proposed dataset was changed. There was a problem with the access through the proxy username to access the CMIP6 data. Therefore, I changed to a CDS dataset. Some data stores are better than others, regarding documentations and ease of access.
2. The volume of the downloaded data had to be considered for the election of the uploaded query. If the sentinel 3 data was chosen, the volume was too large. Therefore, an older timespan was selected, which used a different satellite with lower spatial resolution. Also, time was limited to only one month to ensure that the output file was not too large.
3. Error in pushing changes due to trying to push .nc file (without noticing). This caused the necessity to remove this file from history and create a gitignore file before pushing again.
4. Data is unreadable due to downloaded file being apparently zipped. Used Google Gemini to identify this problem and insert the code lines for uncompressing it. Make sure to exclude all .nc files from push requests by adding this to gitignore file. 





### **Scalability**



Scalability for the download of albedo data using this script is fairly straightforward. To avoid any problem, the cds provides a api request code generator (https://cds.climate.copernicus.eu/datasets/satellite-albedo?tab=download) and directly substitute into the corresponding cell. Make sure to explicitly clarify the data format for the downloaded set.



However, when trying different settings, it was possible to see that some queries take a long time to be processed. This is due to the size of the solicited data, which should be regarded as a potential limit for larger datasets or downloading data for a longer time period.



An alternative to making the process more efficient would be to create a loop to download data month by month, or year by year. This process could be further parallelized, in this way ensuring that it is more efficient. It would be important to implement a unique name generation scheme in this loop so that the output files are all unique.





### **Author**



Nagibe Maroun González, Universität zu Köln, December 2025



### Reference



Copernicus Climate Change Service, Climate Data Store, (2018): Surface albedo 10-daily gridded data from 1981 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.ea87ed30 (Accessed on Dec-2025)

