
"""
regrid_healpix.py
 
Regridding helpers: lat-lon grid -> HEALPix grid.
 
We do a simple bilinear interpolation from ERA5 (regular lat/lon)
to HEALPix pixel centers for a given NSIDE.
 
Supports:
- 2D DataArray: (latitude, longitude) -> (pixel)
- ND DataArray: (..., latitude, longitude) -> (..., pixel)
 
Notes:
- This is sufficient for the homework (clear, reproducible, works).
"""
 
from __future__ import annotations
 
import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from astropy_healpix import HEALPix
import astropy.units as u
 
 
def healpix_centers_lonlat(nside: int):
    """
    Compute lon/lat (degrees) for all HEALPix pixel centers.
 
    Returns
    -------
    lon_deg : np.ndarray, shape (npix,)
    lat_deg : np.ndarray, shape (npix,)
    """
    hp = HEALPix(nside=nside, order="ring", frame="icrs")
    npix = hp.npix
    ipix = np.arange(npix)
 
    coords = hp.healpix_to_skycoord(ipix)
    lon_deg = coords.ra.to_value(u.deg)
    lat_deg = coords.dec.to_value(u.deg)
    return lon_deg, lat_deg
 
 
def regrid_latlon_to_healpix(
    da: xr.DataArray,
    nside: int,
    lat_name: str = "latitude",
    lon_name: str = "longitude",
) -> xr.DataArray:
    """
    Regrid a DataArray from regular lat-lon grid to HEALPix pixel centers.
 
    Parameters
    ----------
    da : xr.DataArray
        Must include latitude and longitude dimensions.
        Examples:
          - (latitude, longitude)
          - (valid_time, pressure_level, latitude, longitude)
    nside : int
        HEALPix NSIDE (e.g., 8 or 16)
 
    Returns
    -------
    xr.DataArray
        Regridded data with dims (..., pixel)
    """
    lat = da[lat_name].values
    lon = da[lon_name].values
    lon = np.asarray(lon)
 
    # If latitude is descending (common in ERA5), flip it for interpolator
    flip_lat = lat[0] > lat[-1]
    if flip_lat:
        lat_sorted = lat[::-1]
        da_sorted = da.sel({lat_name: lat_sorted})
    else:
        lat_sorted = lat
        da_sorted = da
 
    grid_points = (lat_sorted, lon)
 
    # Target HEALPix pixel centers
    lon_t, lat_t = healpix_centers_lonlat(nside=nside)
    target_points = np.column_stack([lat_t, lon_t])  # (npix, 2)
 
    npix = 12 * nside * nside
 
    # Identify non-lat/lon dims (could be empty for 2D input)
    other_dims = [d for d in da_sorted.dims if d not in (lat_name, lon_name)]
 
    # -------------------------
    # Case 1: 2D input (lat,lon)
    # -------------------------
    if len(other_dims) == 0:
        field2d = da_sorted.values  # shape (lat, lon)
        interp = RegularGridInterpolator(
            grid_points,
            field2d,
            method="linear",
            bounds_error=False,
            fill_value=np.nan,
        )
        out = interp(target_points).astype(np.float32)  # shape (pixel,)
 
        out_da = xr.DataArray(
            out,
            dims=("pixel",),
            coords={"pixel": np.arange(npix)},
            name=f"{da.name}_healpix_nside{nside}" if da.name else f"healpix_nside{nside}",
            attrs=dict(da.attrs),
        )
        out_da.attrs["healpix_nside"] = nside
        out_da.attrs["healpix_order"] = "ring"
        return out_da
 
    # -------------------------
    # Case 2: ND input (...,lat,lon)
    # We'll stack other dims into "sample"
    # -------------------------
    stacked = da_sorted.stack(sample=other_dims)  # dims: (latitude, longitude, sample)
 
    out = np.empty((npix, stacked.sizes["sample"]), dtype=np.float32)
 
    for i in range(stacked.sizes["sample"]):
        field2d = stacked.isel(sample=i).values  # shape (lat, lon)
 
        interp = RegularGridInterpolator(
            grid_points,
            field2d,
            method="linear",
            bounds_error=False,
            fill_value=np.nan,
        )
 
        out[:, i] = interp(target_points).astype(np.float32)
 
    out_da = xr.DataArray(
        out,
        dims=("pixel", "sample"),
        coords={"pixel": np.arange(npix), "sample": stacked["sample"]},
        name=f"{da.name}_healpix_nside{nside}" if da.name else f"healpix_nside{nside}",
        attrs=dict(da.attrs),
    )
 
    out_da = out_da.unstack("sample")
    desired_order = other_dims + ["pixel"]
    out_da = out_da.transpose(*desired_order)
 
    out_da.attrs["healpix_nside"] = nside
    out_da.attrs["healpix_order"] = "ring"
 
    return out_da
