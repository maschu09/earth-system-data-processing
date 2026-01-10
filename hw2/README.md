#### README 

## Author:
## Mohammed Fawaz Nawaz
## Matrikulation No.: 7431597
## ESDP1 WS 2025/26

# ESDP1 – Homework Assignment #2  
**Processing Chain for ERA5 Data, HEALPix Regridding, and Zarr Storage**
 
---
 
## 1. Overview
 
This homework implements a complete daily processing chain for atmospheric
reanalysis data. The workflow is able to:
 
- automatically process daily data,
- support mock downloads for testing,
- download ERA5 specific humidity data,
- regrid the data to HEALPix grids,
- store the results efficiently in Zarr format,
- reload and visualize the processed data.
 
The implementation follows the requirements of **ESDP1 WS 2025/26 – Homework #2**.
 
---
 
## 2. Dataset Description
 
- **Data source:** Copernicus Climate Data Store (ERA5 reanalysis)
- **Variable:** Specific humidity (`q`)
- **Pressure levels:** 975, 900, 800, 500, 300 hPa
- **Temporal resolution:** 6-hourly
- **Time period:** 2024-12-01 to 2024-12-05
- **Original grid:** Latitude–longitude (ERA5 native resolution)
 
---
 
## 3. Workflow Description
 
### 3.1 Daily Control Flow
 
The processing chain is organized on a **daily basis**:
 
- When the pipeline is executed **without arguments**, it automatically:
  - finds the oldest missing day,
  - processes all missing days up to the current date (or configured end date).
- When executed **with a date argument**, only the specified day is processed.
 
Processing status is tracked using `.done` marker files.
 
---
 
### 3.2 Mock Download Mode
 
To test the workflow without downloading real data, a **mock mode** is implemented.
 
Mock mode allows:
- successful downloads,
- simulated download failures,
- mixed successful/unsuccessful runs.
 
This verifies the robustness of the control flow and error handling.
 
---
 
### 3.3 ERA5 Data Download
 
For real processing, ERA5 data are downloaded using the CDS API:
 
- Flexible request definition (no hard-coded user settings inside the download routine)
- Pressure levels and variables can be easily adapted
- Data are downloaded **day-by-day** in NetCDF format
 
---
 
### 3.4 HEALPix Regridding
 
Within each daily batch, the ERA5 data are interpolated from the
latitude–longitude grid to HEALPix grids with two resolutions:
 
- **NSIDE = 8**
- **NSIDE = 16**
 
Regridding is performed **inside the daily processing chain**
(i.e. download → regrid → store).
 
---
 
### 3.5 Zarr Storage Strategy
 
Regridded data are stored in **Zarr format (v2)** to ensure compatibility.
 
#### Chunking strategy:
- `valid_time`: 1 (efficient appending of daily data)
- `pressure_level`: all levels in one chunk
- `pixel`: 512
 
New data are appended along the `valid_time` dimension when the Zarr store
already exists.
 
---
 
## 4. Visualization
 
Two arbitrary time samples (valid_time indices 0 and 2) are loaded from the Zarr
store and compared with the original ERA5 data.
 
### Interpretation:
- The original ERA5 lat–lon plots show large-scale humidity structures.
- The HEALPix plots preserve these spatial patterns despite the change in grid geometry.
- This confirms that the regridding operation is physically consistent.
 
---
 
## 5. How to Run

All commands are executed from the project root directory.

## 5.1 Mock Mode (Testing the Workflow)
The pipeline can be tested without downloading real data by enabling mock processing. This mode is useful to validate the daily control flow and error handling.
Command: python -m src.pipeline
In mock mode:
Dummy files are created instead of real downloads
Successful and failing downloads can be simulated
The pipeline correctly continues processing missing days

## 5.2 Process a Single Day (Real Data)
To process only a specific date, the date can be passed as a command-line argument.
Command: python -m src.pipeline 2024-12-01
This performs the following steps:
Downloads ERA5 data for the specified day
Regrids the data to HEALPix NSIDE=8 and NSIDE=16
Stores the regridded data in Zarr format
Marks the day as completed

## 5.3 Process All Missing Days
When the pipeline is executed without a date argument, it automatically:
identifies the oldest missing day,
processes all missing days up to the configured end date.
Command: python -m src.pipeline

## 6. Repository Structure
esdp1_hw2_clean/
src/
pipeline.py -->       (daily control flow)
config.py -->          (configuration and mock/real switches)
era5_download.py -->   (ERA5 download routines)
regrid_healpix.py -->  (latitude–longitude to HEALPix interpolation)
zarr_store.py -->      (Zarr storage and chunking strategy)
data/
tmp/ -->               (temporary ERA5 NetCDF files)
status/ -->            (daily .done marker files)
zarr/ -->              (Zarr data stores)
ESDP1_HW2.ipynb -->      (testing and visualization notebook)
README.md

## 7. Zarr Chunking Strategy
The following chunking strategy is used for storing the regridded data:
valid_time: 1
This allows efficient appending of daily data.
pressure_level: all levels in one chunk
pixel: 512
This chunking setup balances storage efficiency and data access performance and is well suited for incremental daily processing.

## 8. Results and Visualization
Two arbitrary time samples were selected from the Zarr store and compared with the original ERA5 latitude–longitude data.
The comparison shows that:
large-scale humidity structures are preserved,
the HEALPix regridding is physically consistent,
the daily processing chain works end-to-end.

## Plots
 
The `plots/` folder contains example visual outputs (PNG) illustrating:
- original ERA5 latitude–longitude humidity fields, and
- the corresponding HEALPix regridded fields (NSIDE=8 and NSIDE=16).

## 9. Conclusion
The implemented processing chain fulfills all requirements of the assignment:
daily workflow control,
mock testing,
ERA5 data download,
HEALPix regridding (NSIDE=8 and NSIDE=16),
efficient Zarr storage with appending,
visualization of original and regridded data.
The workflow is modular, reproducible, and easily extensible to other variables or time periods.

## Author:
## Mohammed Fawaz Nawaz
## Matrikulation No.: 7431597
## ESDP1 WS 2025/26
 