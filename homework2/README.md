# Earth System Data Processing - Homework 2

Author: Darya Fomicheva  
Matriculation number: 7447755  
Date: 21 January 2026 

# Introduction

This homework implements a daily data processing pipeline for ERA5 reanalysis data as part of the Earth System Data Processing course.
The goal is to design a reproducible and modular workflow that handles daily data downloads, processing, and archiving with a single command.

The pipeline supports both real data processing and a mock mode that allows testing the control flow without downloading data. When executed without a date argument, the workflow automatically detects the oldest missing day and processes all subsequent days up to the specified end date. Alternatively, a single day can be processed by providing a date argument.

As a concrete use case, ERA5 humidity data on multiple pressure levels is downloaded for a short time period, interpolated to HEALPix grids with two resolutions, and stored incrementally in Zarr format. The resulting dataset is then used to visualize and compare the original and regridded data.

## How to run

- Main workflow is implemented in the Jupyter notebook.
- Configure `START_DATE`, `END_DATE`, and optionally `RUN_DATE`:
  - `RUN_DATE = None` processes from the oldest missing day up to `END_DATE`
  - `RUN_DATE = date(YYYY, MM, DD)` processes only a single day
- Use `MOCK = True` to test the control flow without downloading data.
- For real downloads, `MOCK = False` and valid CDS API credentials are required (`~/.cdsapirc`).

## Section 1: Mock setup – daily control flow

This section implements a mock version of the daily processing pipeline in order to test the control flow without downloading any real data. The goal is to verify daily batching, detection of missing days, failure handling, and recovery behavior before running the full data processing workflow.

The pipeline works on a fixed date range defined by `START_DATE` and `END_DATE`. The behavior depends on the value of `RUN_DATE`. If `RUN_DATE` is set to `None`, the pipeline processes all days starting from the oldest missing day up to the end date. If a specific date is provided, only this single day is processed.

To support incremental processing and safe restarts, a simple state-tracking mechanism is used. Successfully processed days are recorded in the `done` directory, while failed processing attempts are recorded in the `failed` directory. This allows the pipeline to resume processing without repeating completed days.

At this stage, no real data is downloaded. Instead, a mock mode is used in which small placeholder files are created to represent daily input data. Controlled failures can be triggered for selected days using the `MOCK_FAIL_DAYS` parameter in order to test error handling and recovery.

### Mock pipeline tests

The following test scenarios are used to validate the daily control flow:

**Test 1: Run without arguments**  
The pipeline is executed without specifying a date. All days within the configured date range are processed sequentially in mock mode.

**Test 2: Simulated failure and recovery detection**  
A previously completed day is manually removed from the state to simulate a missing day. A failure is then triggered for this day during processing. The pipeline detects the missing day and attempts to reprocess it, while recording the failure.

**Test 3: Recovery after failure**  
The failure condition is removed and the pipeline is executed again. The previously failed day is successfully processed and marked as completed.

**Test 4: Processing a single day**  
The pipeline is executed with a specific date. In this case, only the selected day is processed.

## Section 2: ERA5 download (daily files)

This section implements the real ERA5 download step for the daily processing chain. For each day in the selected date range (2024-12-01 to 2024-12-05), ERA5 pressure-level humidity data is retrieved in 6-hourly intervals (00, 06, 12, 18 UTC) for the pressure levels 975, 900, 800, 500, and 300 hPa in the original lat–lon resolution.

The download routine is implemented in a flexible way: all dataset-specific settings (dataset name, variable, pressure levels, time steps, and output format) are stored in a configuration dictionary (`ERA5_CFG`) and passed to the download function. The function `era5_download(day, cfg, out_dir)` downloads data for a single day and returns the path to the resulting file. This makes it easy to adapt the workflow to other ERA5 variables or pressure levels without modifying the download routine itself.

In this implementation, the data is retrieved from the CDS API using `cdsapi` and stored as NetCDF files (one file per day) for easier downstream processing.

After downloading the ERA5 data, the resulting NetCDF file is opened with xarray to verify that the dataset was downloaded correctly and to inspect its structure.

## Section 3: Regridding to HEALPix

In this section, the ERA5 data is interpolated from the original regular latitude–longitude grid to a HEALPix grid. The regridding is performed within the daily processing workflow, i.e. each daily file is processed independently and not aggregated before interpolation, as required by the assignment.

The interpolation is implemented using the `astropy-healpix` library, which provides a convenient and well-tested interface for working with HEALPix grids. For a given HEALPix resolution defined by the `NSIDE` parameter, the corresponding pixel centers are computed and mapped to the nearest grid points of the original latitude–longitude grid.

A nearest-neighbor approach is used for simplicity and robustness. For each HEALPix pixel, the closest latitude and longitude indices of the source grid are determined and the corresponding values are selected. Special care is taken to correctly handle descending latitude coordinates and longitude normalization.

The regridding is applied to two different HEALPix resolutions, as required:
- `NSIDE = 8`
- `NSIDE = 16`

The output of the regridding step is an `xarray.DataArray` with a one-dimensional `pixel` dimension, which is suitable for further processing and storage in Zarr format.

## Section 4: Zarr storage and chunking (incremental daily writes)

This section stores the regridded HEALPix data in a persistent Zarr store and defines a chunking strategy that is suitable for time-series data. Saving is performed within the daily processing chain: each processed day is converted to HEALPix (NSIDE=8 and NSIDE=16) and written to the Zarr store immediately, without waiting for all days to finish.

### Dataset structure
For each day, the lat–lon ERA5 dataset is converted into a single `xarray.Dataset` containing two variables:
- `humidity_hp8`  with dimension `pixel_hp8`
- `humidity_hp16` with dimension `pixel_hp16`

Latitude/longitude coordinates are dropped after regridding to avoid merge conflicts, since HEALPix pixels do not share the same lat–lon coordinate structure across different NSIDE values.

### Chunking strategy
The Zarr store is chunked to support efficient access by time and pressure level while keeping pixel dimensions reasonably sized:
- `time`: stored as a small daily block (4 timesteps per day)
- `level`: stored as a full block (all 5 pressure levels)
- `pixel_hp8` and `pixel_hp16`: chunked with a size of 512 pixels

Pixel dimensions are chunked with a size of 512 as a practical trade-off between I/O efficiency and memory usage.

### Append / insert behavior
The writing routine supports incremental updates:
- If the Zarr store does not exist, it is created.
- If it already exists, the new daily data is merged along the `time` dimension.
  Duplicate timestamps are removed while keeping the newest values ("new data wins"), and the store is rewritten.

This implements the required behavior of appending new data and inserting or overwriting overlapping time steps when necessary.

After writing, the Zarr store can be opened with `xarray.open_zarr(...)` to verify the resulting dataset structure and contents.

## Section 5: Loading from Zarr and plotting (original vs. regridded)

This section demonstrates the final output of the processing chain by reading the processed data from the Zarr store.

Two different timestamps are selected directly from the Zarr time coordinate. For each sample, we plot:
- **Original (lat–lon):** the ERA5 field on its native latitude–longitude grid.
- **Regridded (HEALPix):** the corresponding HEALPix slice loaded from Zarr, visualized as a lon/lat scatter plot of HEALPix pixel centers (here for NSIDE=16; NSIDE=8 is stored analogously).

This provides a qualitative comparison between the original gridded field and the regridded HEALPix representation, and confirms that arbitrary time samples can be accessed from the Zarr dataset.
