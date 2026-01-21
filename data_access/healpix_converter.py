import xarray as xr
import healpy as hp
import numpy as np

def latlon_to_healpix(data, lats, lons, nside, nest=False):
    """
    Interpolate lat-lon gridded data to HEALPix grid.
    
    Parameters:
    -----------
    data : np.ndarray
        2D array (lat, lon) or 3D array (time/level, lat, lon)
    lats : np.ndarray
        1D array of latitudes
    lons : np.ndarray
        1D array of longitudes
    nside : int
        HEALPix resolution parameter
    nest : bool
        HEALPix ordering (False = RING, True = NEST)
    
    Returns:
    --------
    healpix_data : np.ndarray
        HEALPix array
    """
    
    # Handle multi-dimensional data
    original_shape = data.shape
    if data.ndim > 2:
        # Flatten extra dimensions, keep lat-lon
        extra_dims = original_shape[:-2]
        data_reshaped = data.reshape(-1, original_shape[-2], original_shape[-1])
    else:
        data_reshaped = data[np.newaxis, :, :]
        extra_dims = ()
    
    # Create 2D meshgrid
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    # Number of HEALPix pixels
    npix = hp.nside2npix(nside)
    
    # Initialize output
    n_samples = data_reshaped.shape[0]
    healpix_data = np.zeros((n_samples, npix))
    pixel_counts = np.zeros(npix)
    
    # Convert lat-lon to HEALPix colatitude and longitude
    theta = np.radians(90.0 - lat_grid)  # colatitude
    phi = np.radians(lon_grid)            # longitude
    
    # Get HEALPix pixel index for each lat-lon point
    pix_indices = hp.ang2pix(nside, theta, phi, nest=nest)
    
    # Aggregate values into HEALPix pixels
    for i in range(n_samples):
        data_slice = data_reshaped[i, :, :]
        
        # Use bincount for efficient aggregation
        # Sum values in each pixel
        healpix_data[i, :] = np.bincount(
            pix_indices.ravel(), 
            weights=data_slice.ravel(),
            minlength=npix
        )
        
    # Count how many lat-lon points fall in each pixel
    pixel_counts = np.bincount(pix_indices.ravel(), minlength=npix)
    
    # Average (avoid division by zero)
    mask = pixel_counts > 0
    healpix_data[:, mask] /= pixel_counts[mask]
    
    # Mark empty pixels (if any) as NaN
    healpix_data[:, ~mask] = np.nan
    
    # Reshape back to original extra dimensions
    if extra_dims:
        healpix_data = healpix_data.reshape(extra_dims + (npix,))
    else:
        healpix_data = healpix_data[0, :]
    
    return healpix_data


def create_healpix_dataset(ds_latlon, nside):
    """
    Convert lat-lon dataset to HEALPix dataset with multiple variables.
    """
    npix = hp.nside2npix(nside)
    
    # Get coordinates
    lats = ds_latlon.latitude.values
    lons = ds_latlon.longitude.values
    
    # Dictionary to store HEALPix variables
    data_vars = {}
    
    # Convert each variable
    for var_name in ds_latlon.data_vars:
        print(f"Converting {var_name} to HEALPix...")
        hp_data = latlon_to_healpix(
            ds_latlon[var_name].values, 
            lats, 
            lons, 
            nside
        )
        
        # Store with original attributes
        data_vars[var_name] = (
            ['time', 'level', 'pixel'],  # dimensions
            hp_data,
            ds_latlon[var_name].attrs    # keep metadata
        )
    
    # Create new dataset with HEALPix structure
    ds_healpix = xr.Dataset(
        data_vars=data_vars,
        coords={
            'time': ds_latlon.valid_time.values,
            'level': ds_latlon.pressure_level.values,
            'pixel': np.arange(npix)
        },
        attrs={
            'healpix_nside': nside,
            'healpix_order': 'RING',
            'source': 'ERA5 regridded to HEALPix'
        }
    )
    
    return ds_healpix
