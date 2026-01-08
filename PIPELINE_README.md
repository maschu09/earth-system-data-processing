# Earth System Data Processing

Complete pipeline for downloading, processing, and archiving ERA5 climate data.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure CDS API Credentials
Create `~/.cdsapirc`:
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR_KEY_HERE
```

### 3. Run Pipeline with Mock Data (Test Workflow)
```bash
cd data_access
python era5_pipeline.py --mock
```

### 4. Run Pipeline for Real (Download Data)
```bash
# Process specific date
python era5_pipeline.py 2024-12-01

# Process date range
python era5_pipeline.py --start 2024-12-01 --end 2024-12-05

# Process all missing files up to today
python era5_pipeline.py

# Find oldest missing and process from there
python era5_pipeline.py --find-missing
```

## Pipeline Overview

The pipeline handles **three core operations** triggered by a single command:

1. **Download**: Fetch ERA5 humidity data from Copernicus Climate Data Store
   - 6-hourly intervals (00:00, 06:00, 12:00, 18:00)
   - Pressure levels: 975, 900, 800, 500, 300 hPa
   - Original lat-lon resolution
   - NetCDF format

2. **Processing**: Apply data transformations
   - Extensible framework for custom processing logic
   - Quality checks, regridding, unit conversions, etc.

3. **Archiving**: Organize processed files by date
   - Timestamped directory structure
   - Long-term storage organization

## Smart Workflow Features

✅ **Automatic Gap Detection**: Finds oldest missing file and continues processing  
✅ **Idempotent Processing**: Skip existing files, no re-processing  
✅ **Flexible Date Control**: Single date, date range, or auto-detect missing  
✅ **Mock Testing**: Test entire workflow without downloading data  
✅ **Comprehensive Logging**: Track all operations in timestamped logs

## Configuration

All user settings are in `data_access/config.py`:

```python
# Data parameters
ERA5_CONFIG = {
    "variable": "relative_humidity",        # Easy to change to temperature, etc.
    "pressure_levels": [975, 900, 800, 500, 300],  # Customize pressure levels
    "times": ["00:00", "06:00", "12:00", "18:00"],  # Customize time intervals
    "format": "netcdf",                     # or "grib"
    "grid": None,                           # None = original lat-lon resolution
}

# Date range
DEFAULT_START_DATE = datetime(2024, 12, 1)
DEFAULT_END_DATE = datetime(2024, 12, 5)
```

**No hardcoding** - modify one file to adapt to different variables, pressure levels, resolutions!

## Project Structure

```
earth-system-data-processing/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── data_access/
│   ├── README.md               # Detailed ERA5 pipeline documentation
│   ├── config.py               # User-configurable settings
│   ├── download.py             # Flexible ERA5 download routine
│   ├── processing.py           # Processing and archiving
│   ├── era5_pipeline.py        # Main control flow script
│   ├── test_mock_pipeline.py   # Test suite
│   ├── logs/                   # Operation logs (created at runtime)
│   ├── data/era5/              # Downloaded files (created at runtime)
│   ├── processed/era5/         # Processed files (created at runtime)
│   └── archive/era5/           # Archived files (created at runtime)
├── LICENSE
└── .git/

```

## Examples

### Process with Default Settings
```bash
cd data_access
python era5_pipeline.py
```
Processes from 2024-12-01 to 2024-12-05 (or to today), finding oldest missing file.

### Process Specific Date
```bash
python era5_pipeline.py 2024-12-01
```
Downloads and processes only December 1, 2024.

### Process Custom Date Range
```bash
python era5_pipeline.py --start 2024-11-01 --end 2024-12-31
```
Processes November 1 - December 31, 2024.

### Test Complete Workflow (No Download)
```bash
python era5_pipeline.py --mock
```
Creates mock files and tests entire processing pipeline without downloading.

### Run All Tests
```bash
python test_mock_pipeline.py
```
Runs full test suite including single date, date range, and missing file detection.

## Customization Examples

### Download Temperature Instead of Humidity
Edit `data_access/config.py`:
```python
ERA5_CONFIG = {
    "variable": "temperature",
    ...
}
```

### Use Different Pressure Levels
Edit `data_access/config.py`:
```python
ERA5_CONFIG = {
    "pressure_levels": [1000, 925, 850, 700, 500, 300, 200],
    ...
}
```

### Use GRIB Format Instead of NetCDF
Edit `data_access/config.py`:
```python
ERA5_CONFIG = {
    "format": "grib",
    ...
}
```

### Add Custom Processing Logic
Edit `data_access/processing.py` `process_daily_data()` function to add:
- Regridding with xarray
- Unit conversions
- Data quality checks
- Merging with other datasets
- Statistical analyses

## Data Output

### Directory Structure
```
archive/era5/2024/12/
├── processed_era5_relative_humidity_20241201.nc
├── processed_era5_relative_humidity_20241202.nc
├── processed_era5_relative_humidity_20241203.nc
├── processed_era5_relative_humidity_20241204.nc
└── processed_era5_relative_humidity_20241205.nc
```

### File Format
- **Variable**: Relative humidity (or specified variable)
- **Dimensions**: Time (4 per day) × Latitude × Longitude
- **Coordinates**: Latitude, Longitude, Pressure levels, Time
- **Format**: NetCDF 4 (default) or GRIB (configurable)

## Monitoring & Debugging

### View Active Logs
```bash
tail -f data_access/logs/pipeline.log
tail -f data_access/logs/download.log
tail -f data_access/logs/processing.log
```

### Check Download Status
```bash
ls -la data_access/data/era5/
```

### Check Processed Files
```bash
ls -la data_access/archive/era5/
```

## Performance

- **Download**: ~30 seconds per daily file (depends on internet/CDS load)
- **Processing**: ~1 second per file (placeholder implementation)
- **Batch processing**: 5 days ≈ 2-3 minutes with default settings

## Troubleshooting

**CDS API Error**: Ensure `~/.cdsapirc` is configured correctly  
**No output**: Check `logs/` directory for error messages  
**Files not downloading**: CDS server may be busy; retry after a few minutes  
**Mock tests failing**: Ensure write permissions in project directory

## Next Steps

1. **Set up CDS credentials** (see Quick Start #2)
2. **Test with mock mode**: `python era5_pipeline.py --mock`
3. **Download real data**: `python era5_pipeline.py --start 2024-12-01 --end 2024-12-05`
4. **Customize processing**: Edit `data_access/processing.py` for your specific needs
5. **Schedule with cron**: `0 2 * * * cd /path/to/project && python data_access/era5_pipeline.py`

## References

- [Copernicus CDS ERA5 Documentation](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels)
- [ERA5 Variables Guide](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation)
- [CDS API Documentation](https://cds.climate.copernicus.eu/api-how-to)

## License

See LICENSE file.

## Author

Created for Earth System Data Processing Project
