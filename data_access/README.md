# ERA5 Data Processing Pipeline

**Author:** Yeganeh Khabbazian  
**Date:** January 2026
**Tool:** Used GitHub Copilot
---

## Overview

This project implements an automated pipeline to download ERA5 climate reanalysis data from the Copernicus Climate Data Store, regrid it to HEALPix equal-area spheres, and store it efficiently in zarr format for time-series analysis.

**What the pipeline does:**

- **Downloads** daily ERA5 data (6-hourly timesteps) via the CDS API, with mock mode for testing
- **Interpolates** every timestep from lat-lon to HEALPix (NSIDE=8 for 768 pixels, NSIDE=16 for 3,072 pixels)
- **Appends immediately** to per-variable zarr stores as part of the daily processing chain
- **Archives** processed files under `archive/YYYY/MM/` after successful processing
- **Validates completeness** by checking zarr time entries before skipping a date

**Key design choices:**

- Mock and real files are kept separate (`data/mock/` vs `data/real/`) to avoid test/production interference
- If the configured variable name isn’t present in a file, the pipeline falls back to the first data variable it finds (for ERA5 this can be the short name `r`).
- Surface variables (no pressure-level dimension) are treated as a single implicit level
- All timestamps are normalized to UTC with `datetime64[ns]` precision
- The zarr base directory is resolved from the git project root (avoiding per-CWD duplicates) and lives at `zarr_data/` one level above `data_access/`
- Daily chunking aligns with the daily processing and completeness-checking workflow

---

## Dataset Information: ERA5

**ERA5** (ECMWF Reanalysis v5) is the state-of-the-art global climate reanalysis from the European Centre for Medium-Range Weather Forecasts. It blends observations (satellites, weather stations, aircraft) with model data via advanced data assimilation.

| Property | Details |
|---|---|
| **Spatial resolution** | ~31 km on regular latitude-longitude grid |
| **Temporal resolution** | Hourly; this pipeline uses 6-hourly (4 times per day) |
| **Variables** | 200+ including temperature, humidity, wind, pressure |
| **Pressure levels** | 37 levels from surface to stratosphere |
| **Coverage** | Global (0–360° longitude, −90–90° latitude) |
| **Data latency** | ~3 months behind real-time |

**Sources:**
- ECMWF ERA5: https://www.ecmwf.int/en/research/climate-reanalysis/era5
- CDS: https://cds.climate.copernicus.eu
- Hersbach et al. (2020): https://doi.org/10.1002/qj.3803

## Understanding HEALPix Grids

### What is HEALPix?

**HEALPix** is a genuinely curvilinear partition of the sphere into exactly equal-area quadrilaterals of varying shape. The base-resolution comprises twelve pixels in three rings around the poles and equator. The resolution of the grid is expressed by the parameter NSIDE, which defines the number of divisions along the side of a base-resolution pixel needed to reach a desired high-resolution partition. All pixel centers are placed on 4 × NSIDE − 1 rings of constant latitude and are equidistant in azimuth (on each ring).

*Source: Gorski et al. (2005), https://arxiv.org/pdf/astro-ph/9905275*

### Used Two Resolutions

The pipeline outputs NSIDE=8 and NSIDE=16:

| Resolution | NSIDE | Pixels | Area per Pixel |
|---|---|---|---|
| **Coarse** | 8 | 768 | ~827 km² |
| **Fine** | 16 | 3,072 | ~207 km² |

### Interpolation Method

Data is regridded from ERA5's regular lat-lon grid to HEALPix using linear interpolation via `scipy.griddata()`. To prevent artifacts at the 0°/360° dateline, where lon=359° and lon=1° are physically adjacent, I duplicate source points with lon±360° shifts. This allows the interpolator to correctly find neighbors across the dateline, eliminating seams in the HEALPix output.

---

## Zarr Storage Format

Zarr stores N-dimensional arrays as a directory of small chunk files plus metadata. This makes it well-suited for time series pipelines because new timesteps can be appended without rewriting the whole dataset, and subsets of the data can be read efficiently. In this project, the main array is stored as `(time, pressure_level, npix)` and chunked by day so that each chunk contains one full daily field (4 timesteps/day). For the 5-day example, this results in an array of shape `(20, 5, 768)` for NSIDE=8 with a daily chunk shape of `(4, 5, 768)`. The store metadata (`zarr.json`) records the chunking and the codec pipeline used to store the data.
Each .zarr directory represents one array store. Inside the store, the data/ directory contains the chunked array values, while time/ and pressure_level/ store the corresponding coordinate arrays. 
Chunk files are organized by chunk indices. With daily chunking (4 timesteps per chunk), chunk index 0 contains the first day of data, chunk index 1 the second day, and so on. This layout allows new days to be appended efficiently without rewriting existing data.
---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Virtual environment** (venv recommended)
- **CDS API key** (only for real downloads)

### Installation

1. Create and activate a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Configure the CDS API for real downloads.

**CDS API setup** (for real mode only):
1. Register free account: https://cds.climate.copernicus.eu
2. Get API key from Profile 
3. Create `~/.cdsapirc`:
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_UID:YOUR_API_KEY
```


### Quick Start: Mock Mode Test

No API setup required:

```bash
cd data_access
jupyter notebook era5_workflow.ipynb
```

In the notebook:
- Cell 3 has `MOCK_MODE = True` by default
- Run all cells 
- Pipeline completes in ~5 seconds with synthetic data
- Check results in `data/mock/`, `processed/mock/`, `archive/`, and `../zarr_data/`

---

## Notebook Usage

The notebook is configured entirely in **Cell 3** (User Parameters):

```python
MOCK_MODE = True                    # True = test, False = real CDS API
ERA5_CONFIG = {
    'variable': 'relative_humidity',
    'pressure_levels': [975, 900, 800, 500, 300],
    'times': ['00:00', '06:00', '12:00', '18:00'],
    'format': 'netcdf',
    'grid': None,                   # None = global; [N, W, S, E] = region
}
single_date = None                  # Set to process one date
start_date = None                   # Set for date range start
end_date = None                     # Set for date range end
```

**Invocation modes (automatic):**

| Configuration | Behavior |
|---|---|
| All `None` (default) | Runs the fixed default range (2024-12-01 to 2024-12-05), as required by the assignment |
| `single_date` set | Processes exactly one date |
| `start_date` & `end_date` set | Processes entire date range |


---

## Output Structure

```
data_access/
  ├── data/
  │   ├── mock/              # Test files (when MOCK_MODE=True)
  │   └── real/              # Real downloads (when MOCK_MODE=False)
  ├── processed/             # Processed copies before archiving(temporary storing)
  │   ├── mock/
  │   └── real/
  ├── archive/               # Final files, organized by date
  │   ├── mock/YYYY/MM/
  │   └── real/YYYY/MM/
  ├── results/               # Saved comparison plots
  └── (parent dir)
      └── zarr_data/         # HEALPix regridded data
          ├── mock/
          │   ├── relative_humidity_nside8.zarr
          │   └── relative_humidity_nside16.zarr
          └── real/
              ├── relative_humidity_nside8.zarr
              └── relative_humidity_nside16.zarr
```

The zarr stores contain:
- **data**: (time, pressure_level, healpix_pixel) array
- **time**: Timestamps as datetime64[ns]
- **pressure_level**: Pressure levels in hPa
- **attrs**: Metadata (nside, variable, pixel count)

---

## Testing & Validation
I first ran the notebook for a single date (02.12.2024).  
Next, I ran the notebook for 01–03 December to confirm that previously downloaded dates are skipped.  
Then I ran the notebook with no arguments and interrupted the download to confirm the pipeline detects download failures.  
I also interrupted the notebook while it was writing Zarr to confirm a rerun attempts the Zarr write again.  
The process for 02.12.2024 took about 25 minutes; I interrupted the internet and checked what happens. It automatically reconnected and continued after 2 minutes. 


### File Validation

Before reusing an existing downloaded file, the pipeline validates that it can be opened and contains expected coordinates (latitude/longitude). Invalid files are deleted and automatically re-downloaded on the next run.

---

## Design Decisions & Robustness

**1. Mock vs Real Separation**

Early testing revealed a critical issue: mock placeholder files would prevent real downloads when switching modes. I solved this by storing mock and real files in separate directories (`data/mock/` vs `data/real/`). This allows seamless testing and switching without manual file cleanup.

**2. Completeness Checking**

Simply checking if an archived file exists is insufficient; interrupted downloads leave partial data. I implemented `check_day_completeness()`, which verifies that all expected timesteps (e.g. 4 for 6-hourly data) exist in the zarr time coordinate before deciding to skip a date. This handles network interruptions gracefully: rerunning the pipeline automatically reprocesses incomplete days.

**3. Variable Name Fallback**

ERA5 uses short variable names (e.g., `r` for relative humidity) that don't always match the long names in `ERA5_CONFIG`. I added automatic detection: if the configured name is not found, the pipeline uses the first data variable with lat/lon dimensions. 

**4. Timestamp Precision**

Zarr time comparisons failed silently when numpy timestamps had different precisions. I now normalize all timestamps to `datetime64[ns]` before storage and comparison, ensuring reliable matching across runs.

**5. Pressure Level Integrity**

When a zarr store already exists, the pipeline verifies that incoming `pressure_levels` match the stored `pressure_level` metadata. If they differ, the write is rejected to prevent mixing incompatible datasets.

**6. Plot Consistency**

Comparison plots align the original ERA5 lat-lon data with the closest matching Zarr timestamp, so visual checks compare the same hour.

**Colormaps**

I use cmocean because it is designed for geophysical fields and preserves meaningful visual gradients across the full range of values. Some palettes are reasonably robust to color‑vision differences, but not all are fully colorblind‑safe, so for maximum accessibility cividis or viridis can be substituted(color-blind friendly).

Example comparison plots (saved under `data_access/results/`):

![ERA5 vs HEALPix comparison](results/comparison_relative_humidity_real_2024-12-01_12UTC.png)

![ERA5 vs HEALPix comparison](results/comparison_relative_humidity_real_2024-12-03_12UTC.png)

**7. Chunking Strategy**

Zarr arrays are stored as `(time, pressure_level, npix)` with time-based chunking so each chunk contains a full daily field. The current strategy is one day per chunk (4 timesteps/day), which matches the daily processing and completeness checks.
In principle, the data could be chunked both in time and in space. Temporal chunking was chosen because the workflow is organized around daily processing, and day-level reruns and HEALPix use. I also looked into spatial chunking for HEALPix data, especially for the case where users might want to repeatedly analyze a limited geographic region such as Germany or Europe. As discussed in the HEALPix limited-area examples provided by DKRZ, efficient spatial chunking for HEALPix requires keeping larger, structured blocks of pixels rather than selecting only the pixels inside a geographic boundary. In practice, this means storing full chunks that may include data outside the region of interest. Since this project mainly works with global fields and day-level processing, I decided not to implement spatial chunking and instead rely on time-based chunking.

Trade-offs and alternatives:
- **Daily chunks (current)**: easy reprocessing of partial days; clean alignment with daily plots and checks.
- **Multi-day or monthly chunks**: fewer chunk files and less metadata overhead; better for long-range analytics but less convenient for day-level reruns.
- **Fixed timesteps per chunk**: decouples chunking from calendar boundaries and is more robust if the cadence changes in the future.



Initially, I used 3-day chunks, but I switched to 1-day chunks because the workflow is organized around daily processing and it’s more convenient to access or reprocess a single day at a time.

Chunk size also matters. With zstd compression in this project, the required 5-day example results in small Zarr stores (~300 KB for NSIDE = 8 and ~1 MB for NSIDE = 16), and individual daily chunks are on the order of a few tens of kilobytes. For longer time ranges or higher resolutions, chunk sizes would need to be reconsidered.

---

## Reflections on Scalability and Limitations

Storage requirements scale linearly with the number of time steps, pressure levels, and HEALPix pixels. Using float32 data keeps storage manageable, but long time periods or higher spatial resolution would significantly increase disk usage.  
Daily chunking aligns well with the daily processing workflow and simplifies reprocessing of incomplete days. For long time spans, larger chunks (e.g. monthly) could reduce metadata overhead at the cost of reduced day level flexibility.  
Processing time increases with the number of time steps, pressure levels, and especially with HEALPix resolution. Higher NSIDE values significantly increase interpolation cost, making resolution choice a key performance consideration.  
The dominant runtime cost is the spatial interpolation from lat lon grids to HEALPix. For a single day, interpolation takes significantly longer than data download as data download was 1 -2 minutes(not a good network) but the rest took around 20 minutes.  

What fails first?
- Interpolation becomes the bottleneck first as NSIDE and time span grow; `scipy.griddata` is approximately O(N × M) in practice and memory-heavy, recomputes triangulations each timestep, and does not reuse geometry across timesteps.  

What becomes unusable?
- The current daily chunking strategy becomes inefficient for multi-year ranges due to excessive metadata and file counts. Beyond O(10^3) days (a few years at 4 timesteps/day), coarser temporal chunking or chunk consolidation would be required to keep metadata overhead reasonable.  
- Large Zarr stores with many small chunk files become slow to traverse and expensive for filesystem metadata; on shared HPC filesystems this can trigger inode pressure and slow directory operations.  

What assumptions stop holding?
- This workflow is not suitable beyond multi-year ranges without redesign of chunking and interpolation.  
- The interpolation approach assumes per-timestep recomputation is acceptable. At higher NSIDE or longer time series, precomputed interpolation weights or dedicated spherical regridding libraries become necessary.  

Limits to scaling include:  
- **API rate limits** that restrict request throughput.  
- **Network bandwidth** that bounds how fast daily files can be fetched.  
- **Local disk** space and filesystem overhead from many Zarr files.  

Possible improvements:  

-The dominant cost in the current workflow is the repeated spatial interpolation from latitude–longitude grids to HEALPix. Performance could be improved by precomputing interpolation weights and reusing them across timesteps, or by switching to dedicated spherical regridding libraries that are designed for repeated global transforms.

-Interpolation could also be parallelized across timesteps or pressure levels, which would reduce required time for daily processing without changing the overall workflow structure.

-For longer time spans, the current daily chunking strategy could be adjusted. Using coarser temporal chunks (for example monthly) or applying Zarr chunk consolidation would reduce metadata overhead and improve I/O performance at the cost of reduced day-level flexibility.

-Download performance could be improved through limited parallelization of daily requests, as long as API rate limits and fair-use policies are respected.

-If the analysis focuses on a specific geographic region rather than on global fields, the workflow could be adapted to download regional subsets of ERA5 data before interpolation. This would reduce download volume and interpolation cost. The resulting HEALPix data would still need to be handled carefully (for example via masking or partial grids), since HEALPix is primarily designed as a global representation.

-For very large datasets, filesystem performance can become a limiting factor due to the large number of small Zarr files. Using larger chunk sizes, consolidated metadata, or object-storage–oriented backends would help mitigate this issue.

-In this project chunks are stored using zstd compression with a fast default setting(level 0). For larger datasets or long-term storage, the compression level could be adjusted to further reduce disk usage, at the cost of slightly slower write performance.
---

## References

1. Hersbach, H., Bell, B., Berrisfield, P., et al. (2020). The ERA5 global reanalysis. *Quarterly Journal of the Royal Meteorological Society*, 146(730), 1999–2049. https://doi.org/10.1002/qj.3803

2. Gorski, K. M., Hivon, E., Banday, A. J., et al. (2005). HEALPix: A framework for high-resolution discretization and fast analysis of data distributed on the sphere. *The Astrophysical Journal*, 622(2), 759–771. https://doi.org/10.1086/427976

3. ECMWF ERA5 Documentation. https://confluence.ecmwf.int/display/CKB/ERA5:+data+documentation

4. Zarr explanation. https://zarr-specs.readthedocs.io/en/latest/v3/core/index.html

5. healpy Tutorial. https://healpy.readthedocs.io/en/latest/tutorial.html
6. Limited-area HEALPix https://easy.gems.dkrz.de/Processing/healpix/limited_area_healpix.html
---
