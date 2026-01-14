ESDP1 – Homework 1

ERA5 Data Access (Pelin Su Kaplan)


1. Overview

This homework explores how to access a small subset of ERA5 data using the Copernicus Climate Data Store (CDS) API. The goal was to understand the full workflow: selecting the dataset, preparing the API configuration, sending a request, downloading a manageable subset, and performing basic checks with xarray to ensure the data look reasonable.

We work with the ERA5 single levels dataset and focus on three commonly used surface variables:
	10 m u-component of wind (u10)
	10 m v-component of wind (v10)
	2 m temperature (t2m)

To keep the process simple and fast, the domain is restricted to Central Europe and only a few days in early September 2024 are downloaded at synoptic times (00, 06, 12, 18 UTC). The data are saved as NetCDF to make the inspection easier.

The full implementation is in the notebook:
data_access/hw1_pelinsu_era5.ipynb


2. Dataset selection and documentation search

Before settling on ERA5, several datasets from the assignment were briefly considered (e.g. IMERG, Sentinel products, ICON output). ERA5 seemed the most suitable choice because the documentation is more complete and many examples exist for the CDS API.

While reading the CDS documentation, several details needed attention:
	which ERA5 product contains the variables needed (reanalysis-era5-single-levels),
	how bounding boxes are written (CDS expects N, W, S, E),
	how to format temporal selections,
	differences between GRIB and NetCDF files,
	the meaning of metadata keys returned by the API.

During early attempts, GRIB files were downloaded unintentionally because GRIB is the default output. Xarray could not open them, so specifying "format": "netcdf" fixed the issue.

Another mistake was forgetting to set the "grid" parameter. Without it, the output file became unexpectedly large. Setting "grid": "0.25/0.25" produced a manageable file.

These early issues helped clarify how sensitive the CDS API is to formatting and parameter choices.


3. CDS API configuration

Accessing ERA5 through the CDS API required three steps:
	1.	Creating a CDS account and accepting the licence terms.
	2.	Copying the personal API key from the CDS website.
	3.	Storing the key locally in a file named .cdsapirc located in the home directory.

The actual key is not included in this repository for security reasons.

In the notebook, the client is initialized with:


import cdsapi
c = cdsapi.Client()


Once the .cdsapirc file was in the correct place, authentication worked without problems.


4. Building the download request

The final request contains:
	variables: u10, v10, t2m
	product: reanalysis
	format: netcdf
	grid: 0.25/0.25
	bounding box for Central Europe
	selected days in September 2024
	synoptic hours (00/06/12/18)

Problems encountered while building the request included:
	forgetting "format": "netcdf" → GRIB output,
	mixing up bounding box order,
	confusion between valid_time and time metadata,
	VS Code working directory mismatches when locating downloaded files.

After these corrections, the download succeeded.


5. Inspecting the dataset with xarray

The dataset opened cleanly in xarray. Basic inspection showed:
	dimensions: valid_time, latitude, longitude,
	variables: u10, v10, t2m,
	coordinate ranges matching the selected subset,
	metadata such as GRIB centre, conventions, and institution information.

This ensured that the structure of the dataset was correct before plotting.


6. Basic plots and sanity checks

Three simple plots were created to check whether the data behaved realistically.

Time series:
The 2 m temperature time series at a representative grid point showed expected day–night cycles without strange jumps or unrealistic values.

Spatial map:
The map of the u10 wind component at the first timestep displayed stronger winds over the North Sea and weaker winds inland, which is meteorologically plausible.

Histogram:
The distribution of temperature values formed a reasonable bell-shaped pattern with no extreme outliers.

These checks confirm that the downloaded data appear consistent.


7. Difficulties encountered and lessons learned

Several challenges came up during the homework:
	accidentally downloading GRIB instead of NetCDF,
	understanding how grid resolution affects file size,
	learning the correct order for CDS bounding boxes,
	distinguishing between time metadata fields,
	resolving VS Code path/workspace confusion.

Working through these issues provided practical experience with the CDS API, ERA5 documentation, and basic data-validation techniques.


8. Scalability considerations

While this homework focuses on a small dataset, the workflow scales to larger projects. For higher-resolution or longer time ranges:
	downloads should be split into monthly or yearly batches,
	NetCDF may be replaced with more efficient formats such as Zarr,
	parallelization might be helpful,
	configuration settings could be stored in YAML files to avoid hard-coding.


9. How to run this notebook
	1.	Install required Python packages (cdsapi, xarray, numpy, matplotlib).
	2.	Create a .cdsapirc file on the local machine containing the personal CDS API credentials.
	3.	Clone the repository and switch to the branch hw1_pelinsu_era5.
	4.	Run the notebook data_access/hw1_pelinsu_era5.ipynb.


10. Final remarks

This homework provided a clear and practical introduction to accessing ERA5 data through the CDS API, downloading a small subset, and performing initial checks to ensure the data were reasonable. Even though the dataset itself was intentionally small, the workflow closely resembles what is done in real research settings, especially for those beginning to work with atmospheric or climate data.

One of the most valuable aspects for me was the process of understanding and resolving the small issues that appeared along the way. Realising why GRIB could not be opened in xarray, seeing how omitting the grid parameter affected file size, or understanding why the bounding-box order matters all pushed me to look more carefully at the documentation and to think more precisely about how the API request is structured. These moments helped the overall system make much more sense.

Sometimes even simple details—such as the distinction between time and valid_time, or finding where VS Code saved the file—ended up clarifying how different components of the workflow fit together. By the end of the assignment, the logic behind the API request, the structure of the downloaded file, and the meaning of the metadata felt far more intuitive than at the beginning.

In the end, this homework was not only a technical exercise but also a meaningful learning experience. It helped strengthen my understanding of data-access pipelines, early validation steps, and the general structure behind ERA5 and the CDS API. 