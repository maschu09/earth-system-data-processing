import zarr
import xarray as xr
import logging
import os

logger = logging.getLogger(__name__)

def save_healpix_to_zarr(ds_healpix, nside, output_path, mode='w'):
    """
    Save HEALPix dataset to Zarr with chunking.
    
    Parameters:
    -----------
    ds_healpix : xr.Dataset
        Dataset with HEALPix data
    nside : int
        HEALPix resolution
    output_path : str
        Path to Zarr store
    mode : str
        'w' for write (create new), 'a' for append
    """
    
    npix = 12 * nside**2
    chunks = {'time': 20, 'level': 1, 'pixel': npix}
    
    # Apply chunking to dataset
    ds_chunked = ds_healpix.chunk(chunks)
    
    try:
        # Save to Zarr
        ds_chunked.to_zarr(
            output_path,
            mode=mode,
            consolidated=True  # Creates .zmetadata for faster access
        )
        
        store_size = get_zarr_size(output_path)
        logger.info(f"Saved to {output_path} ({store_size})")
        logger.debug(f"Chunks: {chunks}")
    except Exception as e:
        logger.error(f"Failed to save zarr to {output_path}: {type(e).__name__}: {e}")
        raise

def get_zarr_size(path):
    """Get total size of Zarr store."""
    total = 0
    for root, dirs, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return f"{total / 1024**2:.2f} MB"

def append_to_zarr(new_data, zarr_path):
    """
    Append new data using region parameter.
    
    Parameters:
    -----------
    new_data : xr.Dataset
        Dataset to append
    zarr_path : str
        Path to existing zarr store
    """
    try:
        # Open existing store to get current size
        ds_existing = xr.open_zarr(zarr_path)
        current_time_size = len(ds_existing.time)
        
        # Append using region (writes only new data, doesn't reload old)
        new_data.to_zarr(
            zarr_path,
            mode='a',  # append mode
            append_dim='time',
            region={'time': slice(current_time_size, current_time_size + len(new_data.time))}
        )
        logger.debug(f"Appended {len(new_data.time)} timesteps to {zarr_path}")
    except Exception as e:
        logger.error(f"Failed to append to zarr {zarr_path}: {type(e).__name__}: {e}")
        raise