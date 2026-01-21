"""
Configuration file for Homework 2
ERA5 daily processing pipeline
"""

from pathlib import Path


# Base paths


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
ZARR_DIR = DATA_DIR / "zarr"

PLOTS_DIR = BASE_DIR / "plots"

# Ensuring directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
ZARR_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


# ERA5 download configuration


ERA5_PRODUCT = "reanalysis-era5-pressure-levels"

VARIABLES = [
    "specific_humidity"
]

PRESSURE_LEVELS = [
    "975", "900", "800", "500", "300"
]

TIMES = [
    "00:00", "06:00", "12:00", "18:00"
]

DATA_FORMAT = "netcdf"  


# Date range for the homework


START_DATE = "2024-12-01"
END_DATE = "2024-12-05"


# HEALPix configuration


NSIDE_VALUES = [8, 16]


# Zarr configuration


ZARR_STORE_NAME = "era5_specific_humidity_healpix.zarr"

# Chunking strategy
ZARR_CHUNKS = {
    "time": 1,          # daily appends
    "level": -1,        # all pressure levels together
    "healpix": 1024     # safe default, can be tuned
}


# Mock mode (for testing workflow)


USE_MOCK_DOWNLOAD = False
