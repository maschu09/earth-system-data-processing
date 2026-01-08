# ERA5 Data Processing Pipeline

A flexible, production-ready Python pipeline for downloading, processing, and archiving ERA5 climate data with date-based workflow control.

## Features

✅ **Flexible Configuration**: All user settings externalized in `config.py` - no hardcoding  
✅ **Modular Design**: Separate modules for download, processing, and control flow  
✅ **Smart Date Handling**: Automatically finds oldest missing file and continues processing  
✅ **Single-Command Operation**: Trigger download → processing → archiving with one call  
✅ **Multiple Invocation Modes**:
- Process specific date: `python era5_pipeline.py 2024-12-01`
- Process date range: `python era5_pipeline.py --start 2024-12-01 --end 2024-12-05`
- Process all missing files: `python era5_pipeline.py` (default)
- Find oldest missing: `python era5_pipeline.py --find-missing`

✅ **Mock Processing**: Test workflow without downloading data: `python era5_pipeline.py --mock`  
✅ **Comprehensive Logging**: All operations logged to `logs/` directory

## Architecture

```
data_access/
├── config.py              # User-configurable settings (variables, levels, format, dates)
├── download.py            # ERA5 CDS API download routine (flexible, parameterized)
├── processing.py          # Data processing and archiving
├── era5_pipeline.py       # Main control flow script
├── test_mock_pipeline.py  # Test suite for mock processing
├── logs/                  # Log files
├── data/era5/             # Downloaded raw files
├── processed/era5/        # Processed files
└── archive/era5/          # Archived processed files
```

## Configuration

Edit [data_access/config.py](data_access/config.py) to customize:

```python
ERA5_CONFIG = {
    "variable": "relative_humidity",      # CDS variable name
    "pressure_levels": [975, 900, 800, 500, 300],  # hPa
    "times": ["00:00", "06:00", "12:00", "18:00"],  # 6-hourly
    "format": "netcdf",                   # or 'grib'
    "grid": None,                         # None = original lat-lon resolution
}

DEFAULT_START_DATE = datetime(2024, 12, 1)
DEFAULT_END_DATE = datetime(2024, 12, 5)
```

## Download Routine

The `download_era5_daily()` function is fully flexible and parameterized:

```python
from download import download_era5_daily

# Use defaults from config
download_era5_daily(date=datetime(2024, 12, 1))

# Or override with custom parameters
download_era5_daily(
    date=datetime(2024, 12, 1),
    variable="temperature",
    pressure_levels=[850, 700, 500],
    times=["00:00", "12:00"],  # 12-hourly
    output_format="grib",
    grid=[1.0, 1.0]  # 1°×1° resolution
)
```

No user settings are hardcoded within the download routine itself.

## Usage Examples

### 1. Process a Specific Date (with actual download)
```bash
python era5_pipeline.py 2024-12-01
```

### 2. Process Date Range (with actual download)
```bash
python era5_pipeline.py --start 2024-12-01 --end 2024-12-05
```

### 3. Find and Process All Missing Files (with actual download)
```bash
python era5_pipeline.py
```

### 4. Test Mock Processing (no download)
```bash
python era5_pipeline.py --mock
```

### 5. Run Full Test Suite
```bash
python test_mock_pipeline.py
```

## Workflow Steps

For each date processed:

1. **Download**: Fetch ERA5 data from CDS API (6-hourly intervals on specified pressure levels)
2. **Process**: Apply any data processing/transformations (placeholder for custom logic)
3. **Archive**: Move processed files to timestamped archive directory structure

All three steps occur with a single command. If a file already exists, it's skipped.

## Logging

All pipeline operations are logged to:
- **Pipeline log**: `logs/pipeline.log`
- **Download log**: `logs/download.log`
- **Processing log**: `logs/processing.log`

View logs with:
```bash
tail -f logs/pipeline.log
```

## File Organization

Downloaded and processed files are organized by date:

```
data/era5/
├── era5_relative_humidity_20241201.nc
├── era5_relative_humidity_20241202.nc
└── ...

archive/era5/
├── 2024/12/
│   ├── processed_era5_relative_humidity_20241201.nc
│   ├── processed_era5_relative_humidity_20241202.nc
│   └── ...
└── ...
```

## Error Handling

- **Missing files**: Pipeline automatically finds oldest missing file and continues
- **API failures**: Detailed error logging; pipeline skips failed dates and continues
- **Processing errors**: Logged with full traceback; pipeline continues to next date

## Extending the Pipeline

### Add New Variables
Update `config.py`:
```python
ERA5_CONFIG = {
    "variable": "temperature",  # or "geopotential", "wind_speed", etc.
    ...
}
```

### Change Pressure Levels
```python
ERA5_CONFIG = {
    "pressure_levels": [1000, 950, 850, 700, 500, 300, 200, 100],
    ...
}
```

### Change Output Format
```python
ERA5_CONFIG = {
    "format": "grib",  # switch from netcdf
    ...
}
```

### Customize Processing Logic
Edit `processing.py` `process_daily_data()` function to add:
- Regridding
- Unit conversions
- Quality checks
- Data merging

## Testing

Mock processing tests the complete workflow without downloading data:

```bash
python test_mock_pipeline.py
```

Output:
```
======================================================================
ERA5 PIPELINE - MOCK PROCESSING TESTS
======================================================================

TEST: Single date processing (2024-12-01) with mock
...
Result: ✓ PASSED

TEST: Date range processing (2024-12-01 to 2024-12-03) with mock
...
Result: ✓ PASSED

TEST SUMMARY
======================================================================
Total tests: 4
Passed: 4
Failed: 0
======================================================================
```

## Requirements

```
cdsapi
```

Install with:
```bash
pip install -r requirements.txt
```

## CDS API Setup

Before downloading, configure CDS credentials:

1. Register at [CDS portal](https://cds.climate.copernicus.eu/)
2. Create `.cdsapirc` file in home directory:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_KEY_HERE
   ```

## License

See LICENSE file in project root.
