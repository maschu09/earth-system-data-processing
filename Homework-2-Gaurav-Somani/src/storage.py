"""
Zarr storage logic for Homework 2
"""

import xarray as xr
import numpy as np

from config import ZARR_DIR, ZARR_STORE_NAME


def save_healpix_to_zarr(healpix_data, date):
    """
    Save HEALPix data to Zarr.
    """
    date_str = date.strftime("%Y-%m-%d")

    datasets = []

    for nside, data in healpix_data.items():
        ds = xr.Dataset(
            {
                "specific_humidity": ("healpix", data)
            },
            coords={
                "healpix": np.arange(data.size)
            },
            attrs={
                "nside": nside,
                "date": date_str
            }
        )
        datasets.append(ds)

    combined = xr.concat(datasets, dim="nside")

    store_path = ZARR_DIR / ZARR_STORE_NAME
    daily_store = ZARR_DIR / f"era5_healpix_{date_str}.zarr"
    combined.to_zarr(daily_store, mode="w")

