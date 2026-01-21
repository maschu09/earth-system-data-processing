"""
ERA5 daily processing pipeline

Usage:
    python src/main.py
    python src/main.py YYYY-MM-DD
"""

import sys
from datetime import datetime, timedelta

from config import START_DATE, END_DATE
from download import download_era5_day
from process import regrid_to_healpix
from storage import save_healpix_to_zarr


def parse_dates():
    """
    Deciding which dates to process.
    """
    if len(sys.argv) == 2:
        # One date provided
        date = datetime.strptime(sys.argv[1], "%Y-%m-%d")
        return [date]

    # No argument: process full range
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")

    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    return dates


def main():
    dates = parse_dates()

    for date in dates:
        print(f"Processing date: {date.strftime('%Y-%m-%d')}")

        # 1. Download ERA5
        era5_file = download_era5_day(date)

        # 2. Regrid to HEALPix
        healpix_data = regrid_to_healpix(era5_file)

        # 3. Save to Zarr
        save_healpix_to_zarr(healpix_data, date)


if __name__ == "__main__":
    main()
