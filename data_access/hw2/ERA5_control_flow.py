import cdsapi
from datetime import datetime, timedelta
import healpy as hp
import numpy as np
import os
import xarray as xr
    

def retrieve_and_process(dataset, start, end, variable, time, pressure_level, data_format="netcdf", 
                 download_format = "unarchived"):
    """
    Download ERA5 data day by day and interpolate to HEALPix
    """
    
    START_DATE = datetime.strptime(start, "%Y-%m-%d")
    END_DATE   = datetime.strptime(end, "%Y-%m-%d")

    c = cdsapi.Client()

    current = START_DATE
    
    while current <= END_DATE:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\nProcessing: {date_str}")
        
        # Download
        request = {
            "product_type": ["reanalysis"],
            "variable": variable,
            "date": date_str,
            "time": time,
            "pressure_level": pressure_level,
            "data_format": data_format,
            "download_format": download_format
        }
        filename = f"era5_{date_str}.nc"
        
        c.retrieve(dataset, request).download(filename)

        # Load and interpolate
        ds = xr.open_dataset(filename)
        
        # Get grid coordinates
        lats = ds['latitude'].values
        lons = ds['longitude'].values

        lon_grid, lat_grid = np.meshgrid(lons, lats)
        theta = np.radians(90.0 - lat_grid).flatten()
        phi = np.radians(lon_grid).flatten()
        
        # Interpolate to both NSIDE values
        for nside in [8, 16]:
            print(f"  NSIDE={nside}")
            pix_indices = hp.ang2pix(nside, theta, phi)
            npix = hp.nside2npix(nside)
            
            for var_name in ds.data_vars:
                if var_name in ['latitude', 'longitude']:
                    continue
                
                data = ds[var_name].values
                output_shape = list(data.shape[:-2]) + [npix]  # Replace lat,lon with npix
                healpix_map = np.full(output_shape, hp.UNSEEN)
                
                # Flatten spatial dimensions
                data_flat = data.reshape(-1, data.shape[-2] * data.shape[-1])
                healpix_flat = healpix_map.reshape(-1, npix)
                
                # Interpolate each time/level combination
                for i in range(data_flat.shape[0]):
                    valid = ~np.isnan(data_flat[i])
                    counts = np.bincount(pix_indices[valid], minlength=npix)
                    sums = np.bincount(pix_indices[valid], weights=data_flat[i, valid], minlength=npix)
                    mask = counts > 0
                    healpix_flat[i, mask] = sums[mask] / counts[mask]
                
                # Save
                output_file = f"{var_name}_{date_str}_NSIDE{nside}.npy"
                np.save(output_file, healpix_map.reshape(output_shape))
                print(f"    Saved: {output_file}")
        
        ds.close()
        current += timedelta(days=1)