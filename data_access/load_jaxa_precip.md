# Loading the JAXA Precipication Dataset

## Dataset Overview

### 1.1 Dataset Description

The Global Satellite Mapping of Precipitation (GSMaP) is a global precipitation dataset produced by JAXA's Earth Observation Research Center (EORC). The daily gauge-adjusted product provides precipitation estimates at high spatial resolution covering most of the globe.

**Key Specifications:**
- **Spatial Coverage:** Global
- **Spatial Resolution:** 0.1 deg
- **Temporal Coverage:** 2000/03/01 to Present
- **Temporal Resolution:** daily
- **Data Format:** Cloud Optimized GeoTIFF (COG) via JAXA Earth API
- **Units:** Precipitation rate (mm/day)

### 1.2 Data Source and Processing

The GSMaP dataset combines data from multiple satellite sources:
- **Primary Sensors:** Multi-band passive microwave and infrared radiometers
- **Satellites:** GPM Core Observatory and constellation satellites
- **Processing Algorithm:** GSMaP algorithm


**Citations:**

Japan Aerospace Exploration Agency. (1998): GSMaP(Hourly). https://doi.org/10.57746/EO.01gs73bkt358gfpy92y2qns5e9

Kubota, T., et al. (2020): Global Satellite Mapping of Precipitation (GSMaP) products in the GPM era, Satellite precipitation measurement, Springer, https://doi.org/10.1007/978-3-030-24568-9_20

## Gathering Information about the Dataset

On the [JAXA website](https://earth.jaxa.jp/en/data/index.html), one can directly query datasets depending on use, access and relevant information, providing a concise interface to identify the wanted dataset. The sattelite datasets from JAXA can be obtained via __JAXA Earh API__ or __G-Portal__, which are also directly linked on the same page.

### G-Portal
__G-Portal__ seems to be the main access point with the highest level of detail and the biggest selection of datasets. To download datasets from G-Portal, an account needs to be created. In their [documentation](https://gportal.jaxa.jp/gpr/assets/mng_upload/COMMON/upload/GPortalUserManual_en.pdf#page=20.14), it is mentioned that files can be downloaded via SFTP. However, I could not follow their [instructions](https://gportal.jaxa.jp/gpr/assets/mng_upload/COMMON/upload/GPortalUserManual_en.pdf#page=24.12), since it included functionality on the website which was not visible to me. I was thus also unable to follow the [next steps](https://gportal.jaxa.jp/gpr/assets/mng_upload/COMMON/upload/GPortalUserManual_en.pdf#page=27.12), and accessing using a UNIX system (via Colab) did not work. 
There exists, however, a [python interface](https://github.com/sankichi92/gportal-python) for the G-Portal system, which is __unofficial__. Since I did not use this for the main part of this project, will discuss this third-party package later.

Generally, the G-Portal website seems very convoluted, with an outdated documentation-file and does not provide easy access to the required data.

### JAXA Earth API

__JAXA Earth API__ is another access point to some of the datasets JAXA provides. The [website](https://data.earth.jaxa.jp/en/) is structured much more clearly, with a succinct overview over all the datasets and [clear documentation](https://data.earth.jaxa.jp/api/python/) on how to access the data using either Python or JavaScript. Access to the data via this API requires no authentication, just the installation of a python-package, which is also detailed in the [documentation](https://data.earth.jaxa.jp/api/python/v0.1.4/en/quick.html). While there is some documentation on how to use the package, it is not sufficient for technical questions. However, since the zipped package needs to be downloaded anyway, it is possible to simply inspect the code.

The information on the datasets is also readily available. On the main information page for each dataset (here for [Precip (daily)](https://data.earth.jaxa.jp/en/datasets/#/id/JAXA.EORC_GSMaP_standard.Gauge.00Z-23Z.v6_daily)), all relevant information is either mentioned or linked: For example, the [source data](https://eolp.jaxa.jp/GSMaP_Hourly.html) being used to compile the dataset, which contains all relevant technical information.

While it was quite easy to find all relevant information about the dataset and how to use the API, there remains a huge drawback: The API does not provide any endpoints for directly downloading the data. Instead, all data is kept in-memory; there is also a lot of functionality included in the package to directly work with the in-memory data. Despite this, I decided to use the JAXA Earth API to prepare the script, due to the problems with G-Portal described above.

## Dataset formats

The JAXA Earth API provides data in **Cloud Optimized GeoTIFF (COG)** format, which offers several advantages:
- **Cloud-native:** Optimized for streaming and partial reads
- **Standard format:** Compatible with all major GIS software (QGIS, ArcGIS, GDAL)
- **Metadata included:** Georeferencing information embedded in file
- **Efficient:** Supports compression and internal tiling

However, this presents a limitation for our purposes, since it is not possible to directly download the desired data to disk.

# Data Access

## Loading required Data from Server

Loading the data from the API is very straight-forward; you only need to include the relevant parameters in the call and receive a `data` object. Within the package, this object can then be used to run ad-hoc analyses or visualizations, by passing it to an `ImageProcess`. From these, it is also possible to retrieve the raw data as a numpy-array.

## Saving Data

Since it is not possible to directly download the data-files, I wrote functions to save the retrieved data in GeoTIFF files. To make this whole process more secure and resistant to failure, I implemented some additional functionality, such as the chunked-requests. I utilized the `rasterio` package to write the data to file. The data is then saved according to this directory structure:

```<output_dir>/
    <dataset-identifier>/
        <band>/
            <chunk-date>.tif
```

## Loading Data from File

The data from the file can again be read using the `rasterio` package. You then have access to the numpy-array of data, in the same format as it was saved, together with some metadata. The data  can then be used as desired.

## G-Portal third-party package

In the `extra_jaxa_precip.ipynb` notebook, I prepared the code to load the same dataset as from the JAXA Earth API from G-Portal, using the [third-party package](https://gportal.readthedocs.io/en/stable/). In this package, filtering by date and bounding-box is also possible. There does not seem to be a functionality for reducing the resolution of the data, as is possible in the JAXA Earth API. While there exists a resolution-key in the [docs for search parameters](https://gportal.jaxa.jp/gpr/assets/mng_upload/COMMON/upload/GPortalUserManual_en.pdf#page=120.13), setting any value for this did not yield any results. 

# Scaling Up

Here are some considerations when wanting to scale up or adapt the code for retrieval from the __JAXA Earth API__:

## Technical Challenges 

### In-memory data

The JAXA Earth API loads all requested timesteps and spatial subsets into memory at once.
Large requests require significant RAM and can exceed available memory.
The notebook mitigates this through date-chunking, but the API itself offers no streaming or partial-download options. Additionally, the I/O operations intruduced through this extra step may slow down the process more than it needs to.

### File-formats

GeoTIFF is used as the output format, closely matching the API’s COG design.
The current pipeline writes only GeoTIFF; other file-types can be supported by simply adapting the `save_data_to_disk` function.

### Meta-data

The saved files include CRS, transform and bounds.
If future analysis requires other meta-data, the writing routine must be extended.

### Parallelization

Since the data is loaded for each time-frame (daily, montly or yearly) independently, one can parallelize the whole operation across multiple threads, as long as the API itself can handle it.

## Portal challenges

### Dataset Availability

Via G-Portal, many more datasets are available - also the hourly dataset on which this daily dataset is based. It is also possible to (1) download the data directly to disk and (2) specify different file formats (like HDF). It would thus have been nice to be able to use G-Portal directly, which, however, was not possible due to the inconsistencies in website and documentation. While the third-party pip-package seems to work, it is to be used at own risk, since you need to provide your login-credentials when downloading.