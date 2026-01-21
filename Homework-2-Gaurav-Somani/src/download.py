"""
ERA5 download logic for Homework 2
"""

from datetime import datetime
from pathlib import Path

import cdsapi

from config import (
    ERA5_PRODUCT,
    VARIABLES,
    PRESSURE_LEVELS,
    TIMES,
    DATA_FORMAT,
    RAW_DATA_DIR,
)


def download_era5_day(date: datetime) -> Path:
    """
    Download ERA5 data for a single day.
    """
    date_str = date.strftime("%Y%m%d")
    outfile = RAW_DATA_DIR / f"era5_{date_str}.nc"

    if outfile.exists():
        print(f"ERA5 file already exists: {outfile}")
        return outfile

    client = cdsapi.Client()

    client.retrieve(
        ERA5_PRODUCT,
        {
            "product_type": "reanalysis",
            "variable": VARIABLES,
            "pressure_level": PRESSURE_LEVELS,
            "year": date.strftime("%Y"),
            "month": date.strftime("%m"),
            "day": date.strftime("%d"),
            "time": TIMES,
            "format": DATA_FORMAT,
        },
        str(outfile),
    )

    return outfile
