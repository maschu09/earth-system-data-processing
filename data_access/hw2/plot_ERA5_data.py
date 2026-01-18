import xarray as xr
import healpy as hp
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature

ds_hp = xr.open_zarr("era5_nside16.zarr", consolidated=True)

times = ds_hp.time.values[[2, 7]]
sample = ds_hp.sel(time=times)

for t in sample.time.values:
    data = sample['q'].sel(time=t, level=500).values
    hp.mollview(data, title=f"Specific humidity 500 hPa\n{t}")
    plt.show()


ds_nc = xr.open_dataset('era5_2024-12-01.nc', engine='netcdf4')
humidity = ds_nc['q']

# Select data
t_data = humidity.sel(
    pressure_level=500,
    valid_time=times[0]
)

# Create the plot with Robinson projection
fig = plt.figure(figsize=(12, 6))
ax = plt.axes(projection=ccrs.Robinson())

# Plot the temperature field
cf = t_data.plot(
    ax=ax,
    transform=ccrs.PlateCarree(),  # Data is in PlateCarree (lon/lat)
    cmap='coolwarm',
    cbar_kwargs={'label': 'humidity (kg/kg)'},
    add_colorbar=True,
    add_labels=False  # Avoid duplicate labels
)

# Set title
ax.set_title('Plot with netCDF data', fontsize=14, pad=20)

# Add coastlines and country borders
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':')
ax.add_feature(cfeature.LAND, color='lightgray')
ax.add_feature(cfeature.OCEAN, color='lightblue')

# Set global view
ax.set_global()

# Improve layout
plt.tight_layout()  

plt.show()