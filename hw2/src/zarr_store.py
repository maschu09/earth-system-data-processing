
"""
zarr_store.py
 
Helpers for writing and appending data to a Zarr store.
 
We force Zarr format 2 for maximum compatibility with xarray environments.
"""
 
from __future__ import annotations
 
from pathlib import Path
import xarray as xr
 
 
def default_chunks(da: xr.DataArray) -> dict:
    """
    Chunking strategy:
    - valid_time: 1 (good for appending daily)
    - pressure_level: all levels in one chunk (5)
    - pixel: 512 (reasonable)
    """
    chunks = {}
    if "valid_time" in da.dims:
        chunks["valid_time"] = 1
    if "pressure_level" in da.dims:
        chunks["pressure_level"] = da.sizes["pressure_level"]
    if "pixel" in da.dims:
        chunks["pixel"] = 512 if da.sizes["pixel"] >= 512 else da.sizes["pixel"]
    return chunks
 
 
def write_or_append_zarr(
    da: xr.DataArray,
    store_path: Path,
    *,
    var_name: str,
) -> None:
    """
    Write DataArray to Zarr.
    If store exists, append along valid_time.
 
    We force:
    - zarr_format=2 (compatibility)
    - consolidated=False (avoid consolidated-metadata warnings)
    """
    store_path.parent.mkdir(parents=True, exist_ok=True)
 
    da_to_store = da.rename(var_name)
    ds = da_to_store.to_dataset()
 
    chunks = default_chunks(da_to_store)
    ds = ds.chunk(chunks)
 
    if store_path.exists():
        if "valid_time" not in ds.dims:
            raise ValueError("Cannot append: Data must have 'valid_time' dimension.")
        ds.to_zarr(store_path, mode="a", append_dim="valid_time", zarr_format=2, consolidated=False)
    else:
        ds.to_zarr(store_path, mode="w", zarr_format=2, consolidated=False)
