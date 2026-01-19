import cdsapi
from datetime import datetime, timedelta
import healpy as hp
import numpy as np
import xarray as xr
import os
import zarr


def retrieve_and_process(dataset, start, end, variable, time, pressure_level, 
                         data_format="netcdf", download_format = "unarchived"):
    
    # SETUP
    START_DATE = datetime.strptime(start, "%Y-%m-%d")
    END_DATE = datetime.strptime(end, "%Y-%m-%d")
    c = cdsapi.Client()
    current = START_DATE
    
    # DAILY LOOP
    while current <= END_DATE:
        date_str = current.strftime("%Y-%m-%d")
        print(f"\nProcessing: {date_str}")
        
        # DOWNLOAD
        filename = f"era5_{date_str}.nc"
        c.retrieve(dataset, {
            "product_type": ["reanalysis"],
            "variable": variable,
            "date": date_str,
            "time": time,
            "pressure_level": pressure_level,
            "data_format": data_format,
            "download_format": download_format
        }).download(filename)
        

        # INTERPOLATE DATA TO HEALPIX GRID 

        ## Load datafile
        ds = xr.open_dataset(filename)
        
        ## Get time and coordinates, rename to standard names
        if 'valid_time' in ds.coords:
            time_coord = ds['valid_time'].rename({'valid_time': 'time'})
        else:
            time_coord = ds['time']
        
        if 'pressure_level' in ds.coords:
            level_coord = ds['pressure_level'].rename({'pressure_level': 'level'})
        elif 'level' in ds.coords:
            level_coord = ds['level']
        else:
            level_coord = None
        
        ## Implement and convert to healpix grid
        lats, lons = ds['latitude'].values, ds['longitude'].values
        lon_grid, lat_grid = np.meshgrid(lons, lats)
        theta = np.radians(90.0 - lat_grid).flatten()
        phi = np.radians(lon_grid).flatten()
        
        # Interpolate to both NSIDE values
        for nside in [8, 16]:
            print(f"  NSIDE={nside}")
            pix_indices = hp.ang2pix(nside, theta, phi)
            npix = hp.nside2npix(nside)
            zarr_path = f"era5_nside{nside}.zarr"           # create path to store the zarr files
            
            ### loop through variables (here: q for specific humidity)
            data_vars = {}
            for var_name in ds.data_vars:
                if var_name in ['latitude', 'longitude', 'number', 'expver']:
                    continue
                
                data = ds[var_name].values
                healpix_map = np.full(list(data.shape[:-2]) + [npix], hp.UNSEEN, dtype=np.float32)
                data_flat = data.reshape(-1, data.shape[-2] * data.shape[-1])
                healpix_flat = healpix_map.reshape(-1, npix)
                
                for i in range(data_flat.shape[0]):
                    valid = ~np.isnan(data_flat[i])
                    if np.any(valid):
                        counts = np.bincount(pix_indices[valid], minlength=npix)
                        sums = np.bincount(pix_indices[valid], weights=data_flat[i, valid], minlength=npix)
                        healpix_flat[i, counts > 0] = sums[counts > 0] / counts[counts > 0]
                
                # Create DataArray to store data and metadata
                if level_coord is not None and len(level_coord) > 1:
                    data_vars[var_name] = xr.DataArray(
                        healpix_flat.reshape(healpix_map.shape),
                        dims=['time', 'level', 'healpix'],
                        coords={'time': time_coord, 'level': level_coord, 'healpix': np.arange(npix)}
                    )
                else:
                    data_vars[var_name] = xr.DataArray(
                        healpix_flat.reshape(healpix_map.shape),
                        dims=['time', 'healpix'],
                        coords={'time': time_coord, 'healpix': np.arange(npix)}
                    )
            
            # create xarray dataset
            ds_hp = xr.Dataset(data_vars)
            ds_hp.attrs['nside'] = nside
            
            # Save to zarr 
            if os.path.exists(zarr_path):
                # For appending, use append_dim and reconsolidate after
                ds_hp.to_zarr(zarr_path, mode='a', append_dim='time')
                # Reconsolidate metadata after appending
                zarr.consolidate_metadata(zarr_path)
            else:
                # For new files, set up chunking and consolidated metadata
                encoding = {}
                for var in data_vars:
                    if 'level' in ds_hp[var].dims:
                        encoding[var] = {'chunks': (1, len(level_coord), npix)}
                    else:
                        encoding[var] = {'chunks': (1, npix)}
                
                ds_hp.to_zarr(zarr_path, mode='w', encoding=encoding, consolidated=True)
            
            print(f"    Saved to {zarr_path}")
        
        ds.close()
        current += timedelta(days=1)