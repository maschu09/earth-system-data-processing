import zarr
import xarray as xr

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
    
    # Set encoding for compression (optional but recommended)
    encoding = {}
    for var in ds_chunked.data_vars:
        encoding[var] = {
            'compressor': zarr.Blosc(cname='zstd', clevel=3, shuffle=2),
            'dtype': 'float32'
        }
    
    # Save to Zarr
    ds_chunked.to_zarr(
        output_path,
        mode=mode,
        encoding=encoding,
        consolidated=True  # Creates .zmetadata for faster access
    )
    
    print(f"Saved to {output_path}")
    print(f"Chunks: {chunks}")
    print(f"Store size: {get_zarr_size(output_path)}")

def get_zarr_size(path):
    """Get total size of Zarr store."""
    import os
    total = 0
    for root, dirs, files in os.walk(path):
        total += sum(os.path.getsize(os.path.join(root, f)) for f in files)
    return f"{total / 1024**2:.2f} MB"

def append_to_zarr(new_data, zarr_path):
    """
    Append new data using region parameter.
    """
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