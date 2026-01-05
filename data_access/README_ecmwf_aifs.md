# ECMWF AIFS Data Download and Visualization

**Author**: Yeganeh Khabbazian  
**Course**: Earth System Data Processing, University of Cologne, Winter Semester 2025/26  
**Instructor**: Martin Schultz, Jülich Supercomputing Centre & University of Cologne  
**Tools**: Used GitHub Copilot

## Overview

This project demonstrates programmatic access to ECMWF's Artificial Intelligence/Integrated Forecasting System (AIFS) Single deterministic forecast data via the ECMWF Open Data API. 

**About AIFS**: AIFS is a machine learning–based global weather forecasting model operational since February 2025, developed by ECMWF to complement the traditional physics-based Integrated Forecasting System (IFS). The current version was trained on ERA5 reanalysis data (1979–2018) and fine-tuned on operational IFS forecasts (2019–2020), using both pressure-level and surface variables along with auxiliary forcing information such as solar radiation.

**Operational specifications**: AIFS produces global forecasts at 
0.25° × 0.25° resolution four times daily (00, 06, 12, 18 UTC), extending to 15 days ahead in 6-hourly forecast steps. Two operational configurations exist: AIFS Single (deterministic model, operational since 25 February 2025) and AIFS Ensemble (ensemble model, operational since 1 July 2025). This project focuses on AIFS Single surface forecasts. For detailed architecture and training methodology, see the notebook's first cell.

**Note on model execution**: This project downloads pre-generated AIFS forecasts from ECMWF's operational runs. Users interested in running AIFS inference directly or training custom models can use the `anemoi-inference` package with model checkpoints from [HuggingFace](https://huggingface.co/ecmwf/aifs). See [ECMWF's AIFS training documentation](https://anemoi.readthedocs.io/projects/training/en/latest/) for model execution and retraining workflows.

## Repository Content

- **`data_access/AIF.ipynb`**: Main notebook for downloading AIFS Single surface forecasts and creating visualizations
- **`environment.yml`**: Conda environment specification with all dependencies
- **`data_access/aifs_input_output_fields.png`**: AIFS model architecture diagram

## Setup and Execution

### Prerequisites

Create the Conda environment with all required dependencies:

```bash
conda env create -f environment.yml
conda activate aifs
```

The environment includes `earthkit-data` (ECMWF Open Data client), `xarray`/`cfgrib` (GRIB2 file handling), `cartopy` (geospatial visualization), and `eccodes` (GRIB decoding backend).

### Running the Notebook

```bash
jupyter lab data_access/AIF.ipynb
```

## Data Access and Download Scope

The notebook downloads AIFS Single surface forecasts for the **3 most recent complete days** (excluding today) with the following specifications:

- **Spatial coverage**: Global 
- **Temporal resolution**: 12 UTC initialization 
- **Forecast steps**: +6h, +12h, +24h per day
- **Variables**: 2m temperature (2t), 10m winds (10u, 10v), mean sea level pressure (msl)
- **Format**: GRIB2 (WMO standard, ~2.4 MB per file after compression)
- **Total download**: ~22 MB (9 files: 3 days × 3 forecast steps)

The notebook includes a visualization component that generates a global 2m temperature map using a Robinson projection.

**Performance**: Download execution time varies with network speed and ECMWF server load:
- Actual runtime for this project based on my internet around 3 pm: ~90 seconds for 9 files (~22 MB total) I had runs which took a bit more or less time.
- ECMWF Open Data infrastructure demonstrated reliable availability during testing period

### Data Availability Constraints

**ECMWF Open Data** (used in this project):
- Free access, no authentication required
- Retains approximately 4 days of recent forecasts
- Limited to real-time/near-real-time applications

**ECMWF MARS Archive** (for historical access):
- Complete archive dating to operational start (February 2025 for AIFS)
- Requires ECMWF membership, research agreement, or commercial license
- Access via Computing Representative for member state institutions

### Registration and User Experience

**ECMWF Open Data**: No registration required. Access is immediate via public HTTP API
**MARS Archive**: I also tried to access older AIFS data to check whether historical files were available. The request failed with authentication errors, which showed that MARS access is only possible with institutional credentials. Since students without a member-state account or research agreement cannot use the archive, the project had to stay within the 4-day rolling window provided by ECMWF Open Data.

## Development Notes

**Initial approach**: Started with single-day downloads to understand API behavior and file structure. Attempted bulk historical access (1 month), which failed due to ECMWF Open Data retention limits.

**Learning resources**: Attended 3 ECMWF webinars on AIFS data access methods, which clarified:
- Open Data retention policy (~4 days)
- MARS requirements for historical access
- Distinction between web-based visualization (available for older dates) and programmatic API access (limited to recent window)

**Technical implementation**: I first set up the script to download four days of data, including the current day. The first run failed with HTTP errors for today’s files, which showed that the most recent forecast cycle was not fully available yet. After removing the current day, the remaining three days downloaded without issues. To check how far back Open Data goes, I also tested dates older than four days. These requests failed, confirming the ~4-day retention limit. Based on this testing, the most reliable setup is to download the three most recent complete days.

**Key findings**:
- Open Data's 4-day retention limit means you can only access very recent forecasts. Any research requiring historical comparisons or multi-month analysis requires MARS access
- GRIB2 compression achieves ~86% size reduction (compression factor: 0.32 × 0.42 ≈ 0.13) compared to uncompressed theoretical values
- Forecast cycle timing matters: Downloading "today's" data before all 4 daily cycles complete (00, 06, 12, 18 UTC) results in incomplete datasets
- ECMWF provides extensive learning resources: webinars on data access methods, example notebooks on [GitHub](https://github.com/ecmwf/notebook-examples/tree/master/opencharts)


## Scaling Considerations

### Current Limitations
The notebook implements a minimal viable example (22 MB, 3 days). Production applications face several constraints:
1. **Data retention**: Open Data's ~4-day window precludes historical analysis without MARS access
2. **Download efficiency**: Sequential HTTP requests become inefficient at scale (100+ files)
3. **Storage organization**: Flat directory structure unsuitable for more dates and forecast steps
4. **Data volume**: Full AIFS archive (all variables, levels, forecast steps, 4 cycles/day since Feb 2025) exceeds 450 GB

### Script Modifications for Larger Downloads
**Current approach** (Cell 5): Simple `for` loop downloads one file at a time, easy to understand but inefficient for bulk operations.

**Required changes** for production-scale access:
- **Date generation**: Replace `range(1, 4)` loop with `pandas.date_range()` to dynamically generate arbitrary time ranges
- **Parallel execution**: Use `concurrent.futures.ThreadPoolExecutor` to download multiple files simultaneously, reducing execution time.
- **MARS authentication**: For historical access, replace `earthkit.data.from_source()` with `ecmwf-api-client` using institutional credentials to access full archive back to Feb 2025
- **Batch request queuing**: Submit large requests as multiple smaller batches to avoid MARS queue limits and enable graceful retry on individual batch failures
- **Resumable downloads**: Check `Path.exists()` before each download to skip already-retrieved files
- **Robust error handling**: Add `try/except` with exponential backoff to automatically retry failed downloads
- **Progress monitoring**: Add `tqdm` progress bars for real time feedback during multi-hour bulk downloads

### Data Organization at Scale
**Hierarchical storage**: Replace flat directory with `data/{year}/{month}/{day}/{run}/` structure for better filesystem performance and date based queries. For long term analysis, convert GRIB2 to Zarr or NetCDF formats optimized for time series extraction.

**Automated scheduling**: Deploy cron jobs (Linux/Mac) or Task Scheduler (Windows) to run downloads daily, maintaining a rolling archive automatically.

### Technologies for Efficiency
- **Parallel HTTP requests**: `ThreadPoolExecutor` reduces download time 
- **Compression-aware storage**: GRIB2 achieves ~86% size reduction (0.32 × 0.42 compression factor)
- **Cloud-native formats**: Zarr enables chunked, compressed storage with efficient partial reads for analysis
- **Disk space validation**: Check `shutil.disk_usage()` before initiating multi GB downloads

### Limits
**Critical constraint**: ECMWF Open Data retention (~4 days) is the hard limit for free access. Historical data requires institutional MARS credentials (member state affiliation) or commercial license. Students without these credentials cannot access data older than ~4 days, regardless of technical optimizations.



## Data Attribution

ECMWF Open Data are available under the [Creative Commons CC-BY-4.0 license](https://creativecommons.org/licenses/by/4.0/), which requires attribution.

**Attribution for this project**:
> Adapted from "ECMWF AIFS Single 15-day Forecast Data" by ECMWF, licensed under CC BY 4.0, available at https://data.ecmwf.int/forecasts/

For more information on ECMWF Open Data licensing and attribution requirements, see the [ECMWF Open Data announcement](https://www.linkedin.com/posts/ecmwf-users_ecmwf-opendataforecasting-activity-7338934286546358274-aw2K).

## References

- [ECMWF AIFS Documentation](https://www.ecmwf.int/en/forecasts/dataset/aifs-machine-learning-data)
- [AIFS Single Implementation](https://www.ecmwf.int/en/forecasts/documentation-and-support/changes-ecmwf-model/aifs-single-v1-implementation)
- [Machine Learning for Forecasters](https://events.ecmwf.int/event/493/)
- [ECMWF Notebook Examples](https://github.com/ecmwf/notebook-examples/tree/master/opencharts)
- [Earthkit Data Documentation](https://earthkit.readthedocs.io/en/latest/)

## License

See `LICENSE` file for details.