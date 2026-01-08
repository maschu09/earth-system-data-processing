# Quick Reference Guide

## Command Cheat Sheet

```bash
# Test workflow (no download)
python data_access/era5_pipeline.py --mock

# Process specific date
python data_access/era5_pipeline.py 2024-12-01

# Process date range
python data_access/era5_pipeline.py --start 2024-12-01 --end 2024-12-05

# Auto-detect and process missing files
python data_access/era5_pipeline.py

# Find oldest missing file
python data_access/era5_pipeline.py --find-missing

# Run test suite
python data_access/test_mock_pipeline.py

# View pipeline logs
tail -f data_access/logs/pipeline.log

# Check downloaded files
ls -la data_access/data/era5/

# Check archived files
ls -la data_access/archive/era5/
```

## Configuration Quick Reference

### File: `data_access/config.py`

```python
# Change variable
"variable": "temperature"  # or "geopotential", "wind_speed", etc.

# Change pressure levels
"pressure_levels": [1000, 950, 850, 700, 500, 300, 200, 100]

# Change time interval
"times": ["00:00", "12:00"]  # 12-hourly instead of 6-hourly

# Change output format
"format": "grib"  # instead of "netcdf"

# Change grid resolution
"grid": [1.0, 1.0]  # 1°×1° instead of original

# Change date range
DEFAULT_START_DATE = datetime(2024, 1, 1)
DEFAULT_END_DATE = datetime(2024, 12, 31)
```

## Module Functions Reference

### `download.py`
```python
from download import download_era5_daily, find_oldest_missing_file

# Download single date
file_path = download_era5_daily(datetime(2024, 12, 1))

# Download with custom settings
file_path = download_era5_daily(
    date=datetime(2024, 12, 1),
    variable="temperature",
    pressure_levels=[850, 700],
    times=["00:00", "12:00"],
    output_format="netcdf",
    grid=None
)

# Find oldest missing
oldest = find_oldest_missing_file(start, end)
```

### `processing.py`
```python
from processing import process_and_archive, process_daily_data, archive_file

# Process and archive in one call
success = process_and_archive(input_file)

# Or separately
processed = process_daily_data(input_file)
archived = archive_file(processed)
```

### `era5_pipeline.py`
```bash
# All control flow modes available via command line
# See Command Cheat Sheet above
```

## Directory Structure

```
project_root/
├── data_access/
│   ├── config.py                # ← EDIT THIS for settings
│   ├── era5_pipeline.py         # ← RUN THIS for pipeline
│   ├── test_mock_pipeline.py    # ← RUN THIS for tests
│   ├── data/era5/               # ← Downloaded files appear here
│   ├── processed/era5/          # ← Processed files appear here
│   ├── archive/era5/            # ← Archived files organized by date
│   └── logs/                    # ← Log files appear here
├── IMPLEMENTATION_SUMMARY.md    # ← Read for overview
├── PIPELINE_README.md           # ← Read for detailed guide
├── examples.py                  # ← Programmatic usage examples
└── requirements.txt             # ← Install dependencies
```

## Common Tasks

### Process Missing Files Daily (Cron)
```bash
# Add to crontab: Process every day at 2 AM
0 2 * * * cd /path/to/project && python data_access/era5_pipeline.py >> /var/log/era5.log 2>&1
```

### Change to Download Temperature
1. Edit `data_access/config.py`
2. Change: `"variable": "temperature"`
3. Run: `python data_access/era5_pipeline.py --mock`
4. Run: `python data_access/era5_pipeline.py 2024-12-01`

### Use Different Pressure Levels
1. Edit `data_access/config.py`
2. Change: `"pressure_levels": [1000, 850, 500, 200]`
3. Run pipeline with new settings

### Add Custom Processing
1. Edit `data_access/processing.py`
2. Modify `process_daily_data()` function
3. Add your logic (regridding, unit conversion, etc.)
4. Run: `python data_access/era5_pipeline.py --mock`

### Debug Failed Download
1. Check logs: `cat data_access/logs/download.log`
2. Verify CDS credentials: `cat ~/.cdsapirc`
3. Check file exists: `ls data_access/data/era5/`
4. Re-run: `python data_access/era5_pipeline.py 2024-12-01`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `CDS API Error` | Configure `~/.cdsapirc` with your CDS key |
| `No output` | Check `logs/pipeline.log` for errors |
| `File not downloading` | CDS server may be busy, retry later |
| `Permission denied` | Check write permissions in project directory |
| `File already exists` | Pipeline skips existing files; delete and retry |

## Performance Reference

| Operation | Time |
|-----------|------|
| Mock test (1 day) | ~0.5 seconds |
| Mock test (5 days) | ~2 seconds |
| Download 1 day | ~30 seconds |
| Process 1 day | ~1 second |
| Archive 1 day | ~0.1 seconds |
| Batch 5 days | ~2-3 minutes |

## Key Features

✅ **Flexible**: Change variables, levels, format in config file  
✅ **Smart**: Auto-detects missing files  
✅ **Safe**: Won't re-process existing files  
✅ **Logged**: Tracks all operations  
✅ **Tested**: Mock mode for validation  
✅ **Modular**: Use separately or together  
✅ **Documented**: Comprehensive guides included  

---

**For detailed information, see:**
- `IMPLEMENTATION_SUMMARY.md` - Overview
- `PIPELINE_README.md` - Detailed guide
- `data_access/README.md` - Technical reference
