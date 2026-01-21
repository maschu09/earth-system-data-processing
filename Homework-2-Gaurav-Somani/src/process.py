"""
Lat-lon to HEALPix regridding using astropy-healpix
"""

import numpy as np
import xarray as xr

from astropy_healpix import HEALPix
import astropy.units as u

from config import NSIDE_VALUES


def regrid_to_healpix(era5_file):
    """
    Convert ERA5 lat-lon data to HEALPix grids.
    Returns a dictionary keyed by NSIDE.
    """
    ds = xr.open_dataset(era5_file)

    da = ds["q"].sel(pressure_level=800).isel(valid_time=0)


    lat = da.latitude.values
    lon = da.longitude.values

    lon2d, lat2d = np.meshgrid(lon, lat)
    lon_u = lon2d * u.deg
    lat_u = lat2d * u.deg

    values = da.values

    results = {}

    for nside in NSIDE_VALUES:
        hp = HEALPix(nside=nside, order="ring", frame="icrs")

        pix = hp.lonlat_to_healpix(lon_u, lat_u)
        pix_flat = pix.ravel()
        val_flat = values.ravel()

        hp_map = np.full(hp.npix, np.nan)

        for p in np.unique(pix_flat):
            hp_map[p] = np.nanmean(val_flat[pix_flat == p])

        results[nside] = hp_map

    return results
