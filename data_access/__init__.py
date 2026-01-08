"""
ERA5 Data Processing Pipeline
==============================

A flexible, production-ready pipeline for downloading, processing, and archiving
ERA5 climate data with date-based workflow control.

Usage:
    python era5_pipeline.py [date] [--start START] [--end END] [--mock] [--find-missing]

Examples:
    # Process specific date
    python era5_pipeline.py 2024-12-01
    
    # Process date range
    python era5_pipeline.py --start 2024-12-01 --end 2024-12-05
    
    # Process all missing files (default)
    python era5_pipeline.py
    
    # Test with mock processing (no download)
    python era5_pipeline.py --mock

For detailed documentation, see README.md in this directory.
"""

__version__ = "1.0.0"
__author__ = "Earth System Data Processing"

# Import main functions for programmatic use
from download import download_era5_daily, find_oldest_missing_file
from processing import process_daily_data, archive_file, process_and_archive

__all__ = [
    'download_era5_daily',
    'find_oldest_missing_file',
    'process_daily_data',
    'archive_file',
    'process_and_archive',
]
