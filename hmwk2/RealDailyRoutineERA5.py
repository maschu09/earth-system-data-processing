import sys
import os
import cdsapi
from datetime import datetime, timedelta
import numpy as np
import xarray as xr 

 
StartDate = datetime(2024, 12, 1)
EndDate = datetime(2024, 12, 5)
StoreZARR = "era5_humidity.zarr"

# real routines

def check_if_processed(date):
    """
    Checks if a specific date already exists in our Zarr storage.
    """
    # modify!!!
    return os.path.exists(f"mock_storage_{date.strftime('%Y%m%d')}.txt")

def real_daily_data_routine(date,variable, levels, hours):
    """
    Processing chain: Download -> Regrid -> Save
    """
    date_str = date.strftime('%Y-%m-%d')
    tmp_file = f"temp_{date_str}.nc"
    
    print(f"\nStarting pipeline for: {date.strftime('%Y-%m-%d')}")
    
    try: 
        
        print(f"Downloading {variable} for {date_str}...")
        download_era5(date, variable, levels, hours, tmp_file)
        
        print(f"Regridding to HEALPix (NSIDE 8 and 16).") 
        regridded_data = regrid_to_healpix(tmp_file, date_str)
        
        
        print(f"Appending to Zarr store: {StoreZARR}") 
        save_to_zarr(regridded_data, StoreZARR, date_str)
    
        # Success: Mark as done
        with open(f"mock_storage_{date.strftime('%Y%m%d')}.txt", "w") as f:
            f.write("done")
            
        # Clean up the temporary NetCDF file to save space
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
            
        return True

    except Exception as e:
        print(f"Failed processing {date_str}: {e}")
        return False

# download era5
def download_era5(date, variable, levels, hours, targetFile):
    
    dataset = "reanalysis-era5-pressure-levels"
    request = {
        'product_type': 'reanalysis',
        #"data_format": "grib",
        'format': 'netcdf',
        'variable': variable,
        'pressure_level': levels,
        'year': date.strftime('%Y'),
        'month': date.strftime('%m'),
        'day': date.strftime('%d'),
        'time': hours,
        #'download_format': "unarchived"
    }
    
    client = cdsapi.Client()
    client.retrieve(dataset, request, targetFile)


# regridding routine
# temporal fix for not being able to download healpy
try:
    import healpy as hp
    HEALPY_AVAILABLE = True
except ImportError:
    HEALPY_AVAILABLE = False
    print("Warning: 'healpy' not found. Regridding will be skipped.")

def regrid_to_healpix(source_file, date_str, nside_list=[8, 16]):

    if not HEALPY_AVAILABLE:
        print("Skipping regridding (Library missing).")
        return None

    ds = xr.open_dataset(source_file)
    
    # source coords
    lats = ds.latitude.values
    lons = ds.longitude.values
    
    # meshgrid with source coords
    lon_grid, lat_grid = np.meshgrid(lons, lats)
    
    regridded_data = {}
    
    for nside in nside_list:
        print(f"  ... Processing NSIDE={nside}")
        
        # Helapix grid
        npix = hp.nside2npix(nside)
        
        # latitude and longitude for every pixel in radians: 
        #theta (colatitude) and 
        #phi (longitude) 
        theta, phi = hp.pix2ang(nside,np.arange(npix))
        
        # convert to degrees and lat/long
        target_lats = 90.0-np.degrees(theta)
        target_lons = np.degrees(phi)
        
        # INTERPOLATE
        # xarray's .interp() is powerful. We pass the new target coordinates.
        # We need to structure target_lats/lons as xarray DataArrays sharing a 'dim'
        target_lats_da = xr.DataArray(target_lats, dims="healpix_pixel")
        target_lons_da = xr.DataArray(target_lons, dims="healpix_pixel")
        
        ds_healpix = ds.interp(
            latitude=target_lats_da,
            longitude=target_lons_da,
            method="linear")
        
        regridded_data[nside] = ds_healpix

    ds.close()
    return regridded_data

# saving to zarr store

def save_to_zarr(data_dict, store_path, date_str):
    if data_dict is None:
        return # Skip if regridding failed

    for nside, ds in data_dict.items():
        # Define Group Name (e.g., 'NSIDE_8')
        group_name = f"NSIDE_{nside}"
        # chunk by 1 day and keep spatial dims whole or split slightly.
        chunks = {'time': 1, 'healpix_pixel': -1} 
        ds = ds.chunk(chunks)
        
        #check if store exists, a mode for append and w for overwrite
        if not os.path.exists(store_path):
             mode = 'w'
             append_dim = None
        else:
             # check if group exist
             group_path = os.path.join(store_path, group_name)
             if os.path.exists(group_path):
                 mode = 'a'
                 append_dim = 'time'
             else:
                 mode = 'a' # Add new group to existing store
                 append_dim = None

        if append_dim:
            ds.to_zarr(store_path, group=group_name, mode=mode, append_dim=append_dim, consolidated=True)
        else:
            ds.to_zarr(store_path, group=group_name, mode=mode, consolidated=True)
            

    print(f"Data for {date_str} saved to {store_path}")

# control flow

def real_run_control_flow(date_arg=None, variables= 'relative_humidity', 
                          levels= ['300', '500', '800', '900', '975'],
                          hours=['00:00', '06:00', '12:00', '18:00']):
    #date was provided
    if date_arg:
        desired_date = datetime.strptime(date_arg, "%Y-%m-%d")
        real_daily_data_routine(desired_date, variables, levels, hours)
        return

    # no arguments - look for oldest missing file 
    print(f"Scanning for missing data between {StartDate.date()} and {EndDate.date()}...")
    
    current_date = StartDate
    while current_date <= EndDate:
        if not check_if_processed(current_date):
            success = real_daily_data_routine(current_date, variables, levels, hours)
            # Handle successful and unsuccessful downloads 
            if not success:
                print("Stopping --> Routine failed.")
                break 
        else:
            print(f"{current_date.date()} exists --> Skipping.")
        
        current_date += timedelta(days=1)