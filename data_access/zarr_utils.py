import os
import zarr
import shutil
import logging
import numpy as np
import xarray as xr

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
    chunks = {'time': 48, 'level': 1, 'pixel': npix}
    
    # Apply chunking to dataset
    ds_chunked = ds_healpix.chunk(chunks)
    
    try:
        # Save to Zarr
        ds_chunked.to_zarr(
            output_path,
            mode=mode,
            consolidated=True,  # Creates .zmetadata for faster access
            zarr_format=2
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
    Append new data to zarr store.
    
    For your dataset size, we use the simple concatenate-and-rewrite approach.
    """    
    try:
        # Load existing data
        ds_existing = xr.open_zarr(zarr_path).load()
        
        logger.info(f"Existing store has {len(ds_existing.time)} timesteps")
        logger.info(f"Adding {len(new_data.time)} new timesteps")
        
        # Concatenate along time
        ds_combined = xr.concat([ds_existing, new_data], dim='time')
        
        # Remove any duplicate times
        _, unique_indices = np.unique(ds_combined['time'].values, return_index=True)
        ds_combined = ds_combined.isel(time=sorted(unique_indices))
        
        logger.info(f"Combined dataset has {len(ds_combined.time)} timesteps")
        
        # Delete old store
        shutil.rmtree(zarr_path)
        
        # Write combined dataset
        ds_combined.to_zarr(
            zarr_path,
            mode='w',
            consolidated=True,
            zarr_format=2
        )
        
        logger.info(f"✓ Successfully saved combined dataset to {zarr_path}")
        
    except Exception as e:
        logger.error(f"Failed to append to {zarr_path}: {type(e).__name__}: {e}")
        raise
