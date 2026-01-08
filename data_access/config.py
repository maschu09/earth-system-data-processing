"""
Configuration module for ERA5 data processing pipeline.
Contains all user-configurable settings.
"""

from pathlib import Path
from datetime import datetime

# Data download settings
ERA5_CONFIG = {
    # Variable to download (CDS format name)
    "variable": "relative_humidity",
    
    # Pressure levels in hPa
    "pressure_levels": [975, 900, 800, 500, 300],
    
    # Time interval (6-hourly: 00, 06, 12, 18)
    "times": ["00:00", "06:00", "12:00", "18:00"],
    
    # Output format: 'netcdf' or 'grib'
    "format": "netcdf",
    
    # Grid resolution (use None for original lat-lon resolution)
    "grid": None,  # Original resolution
}

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "era5"
PROCESSED_DIR = PROJECT_ROOT / "processed" / "era5"
ARCHIVE_DIR = PROJECT_ROOT / "archive" / "era5"
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, PROCESSED_DIR, ARCHIVE_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Date range for default processing
DEFAULT_START_DATE = datetime(2024, 12, 1)
DEFAULT_END_DATE = datetime(2024, 12, 5)
