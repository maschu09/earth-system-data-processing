import xarray as xr
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

ds_hp = xr.open_zarr("era5_nside16.zarr", consolidated=True)

times = ds_hp.time.values[[2, 7]]
sample = ds_hp.sel(time=times)

## plot 1: regridded data
data = sample['q'].sel(time=times[0], level=500).values
hp.mollview(data, title=f"Specific humidity 500 hPa\n{times[0]}")
plt.show()

## plot 2: regridded data
data = sample['q'].sel(time=times[1], level=500).values
hp.mollview(data, title=f"Specific humidity 500 hPa\n{times[1]}")
plt.show()

#### Plot original netCDF file
ds_nc1 = xr.open_dataset('era5_2024-12-01.nc', engine='netcdf4')
humidity1 = ds_nc1['q']

ds_nc2 = xr.open_dataset('era5_2024-12-02.nc', engine='netcdf4')
humidity2 = ds_nc2['q']

# Select data
t_data1 = humidity1.sel(
    pressure_level=500,
    valid_time=times[0]
)

t_data2 = humidity2.sel(
    pressure_level=500,
    valid_time=times[1]
)

# Create the plot with Robinson projection
fig, (ax1, ax2) = plt.subplots(nrows=1,ncols=2,figsize=(16, 4),subplot_kw={'projection': ccrs.Robinson()})

# Plot the temperature field
cf1 = t_data1.plot(
    ax=ax1,
    transform=ccrs.PlateCarree(),  # Data is in PlateCarree (lon/lat)
    cmap='coolwarm',
    cbar_kwargs={'label': 'humidity (kg/kg)'},
    add_colorbar=True,
    add_labels=False  # Avoid duplicate labels
)

# Set title
ax1.set_title('Plot with netCDF data', fontsize=14, pad=20)

# Add coastlines and country borders
ax1.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax1.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':')
ax1.add_feature(cfeature.LAND, color='lightgray')
ax1.add_feature(cfeature.OCEAN, color='lightblue')

# Set global view
ax1.set_global()

### for 2nd plot
# Plot the temperature field
cf2 = t_data2.plot(
    ax=ax2,
    transform=ccrs.PlateCarree(),  # Data is in PlateCarree (lon/lat)
    cmap='coolwarm',
    cbar_kwargs={'label': 'humidity (kg/kg)'},
    add_colorbar=True,
    add_labels=False  # Avoid duplicate labels
)

# Set title
ax2.set_title('Plot with netCDF data', fontsize=14, pad=20)

# Add coastlines and country borders
ax2.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax2.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':')
ax2.add_feature(cfeature.LAND, color='lightgray')
ax2.add_feature(cfeature.OCEAN, color='lightblue')

# Set global view
ax2.set_global()


# Improve layout
plt.tight_layout()  

plt.show()