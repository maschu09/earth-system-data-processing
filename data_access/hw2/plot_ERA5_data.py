import zarr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

data1 = zarr.open('era5_nside8.zarr')['specific_humidity']
print(data1)