import cdsapi
import healpy as hp
from datetime import datetime, timedelta

import xarray as xr
import numpy as np
import warnings
from pathlib import Path
import zarr
import sys
import re

from IPython.core.display_functions import display
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

#additional packages that are required to run this script are h5netcdf, netcdf4

# <><><><><><><><><><><> CONFIG <><><><><><><><><><><> #

#====== download config ======#
collection='reanalysis-era5-pressure-levels' #this notebook was only tested for the specified collection
product_type=['reanalysis']

variables=['specific_humidity'] # other variables can be found at https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Table9. This notebook was only developed for continues pressure level variables

pressure_levels = [300, 500, 800, 900, 975]

default_temporal_extend = {
    "start": '2024-12-01',
    "end": '2024-12-05',
}

times = ['00:00:00', '06:00:00', '12:00:00', '18:00:00']

spacial_extend = 'global' #for a limited area provide an array of shape [north, west, south, east]. north, south of range [-90, 90] west, east [-180, 180]

data_format = {"format": 'netcdf', "file_ending": '.nc'} # Downstream Processing requires netcdf so only change this variable if you want to change the processing pipeline

grid_res = ['0.25', '0.25'] # [res_long, res_lat] resolution of the grid for the download. The specified 0.25° are the default resolution for atmospheric data in the ERA5 Dataset

#====== storage config =======#

collection_short_name='era5' #short name used for data_storage
storage_path='../data/'
unprocessed_path=f'{collection_short_name}_regular_grid/'
zarr_file=f'{collection_short_name}_healpix.zarr'
zarr_append_dim='time' #in the current state of this script only time makes sense and is the only dimension tested.

#===== regridding config =====#

nsides = [8, 16]
interpolation_method = 'linear' # methode for the interpolation to healpix (one of "linear", "nearest", "zero", "slinear", "quadratic", "cubic", "quintic", "polynomial")

#====== plotting config ======#
plotting_variable_sn='q' # must be the short name of the variable you want to plot. The short names of the variables can be found in the table on the link above.
plotting_pressure_level=975
# <><><><><><><><><><> END CONFIG <><><><><><><><><><> #


def date_check(date_str: str) -> str:
    """
    rudimentary input validation for date strings. Doesn't catch all invalid dates, just some typical typos
    :param date_str:
    :return: date_str if it contains a valid date in format YYYY-mm-dd
    """
    if re.search(string=date_str, pattern='^[1-2][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]$'):
        return date_str
    raise Exception(f'Invalid date String: {date_str} please provide YYYY-mm-dd')


def parse_user_input() -> tuple[str, str]:
    """
    Retrieves user input passed ass args and interprets it as date range information: \n
    no input: 1940-01-01 -> today \n
    YYYY-mm-dd given: that day as start and end date \n
    YYYY-mm-dd--YYYY-mm-dd: [Start]--[End] \n
    YYYY-mm-dd-- or --YYYY-mm-dd: [Start]--today or 1940-01-01--[End] \n
    "assignment": default dates specified in the assignment description
    Some validation is applied but don't rely on it.
    :return: the two date strings
    """
    start = '1940-01-01'
    end = datetime.now().strftime('%Y-%m-%d')
    if len(sys.argv) > 1 and sys.argv[1] is not None:
        date_input = sys.argv[1]
        if date_input == 'assignment':
            start = default_temporal_extend["start"]
            end = default_temporal_extend["end"]
        else:
            splits = date_input.split('--')
            if len(splits) > 2:
                raise Exception('to many dates provided')
            if len(splits) == 2:
                if splits[0] != '':
                    start = date_check(splits[0])
                if splits[1] != '':
                    end = date_check(splits[1])
            else:
                start = date_check(splits[0])
                end = start
    return start, end


def setup() -> None:
    """
    Silences ZarrUserWarnings, and makes sure the required directories exist
    :return:
    """
    warnings.filterwarnings("ignore", category=zarr.errors.ZarrUserWarning)

    if not Path(storage_path).exists():
        Path(storage_path).mkdir()

    if not Path(storage_path + unprocessed_path).exists():
        Path(storage_path + unprocessed_path).mkdir()


def generate_time_chunks(start: str, end: str) -> list[dict]:
    """
    Generates a dict for each day of a date range. The dict has the shape
    {"day": number, "month": number, "year": number, "string": string (format YYYY-mm-dd), "timestamp": np.datetime64}

    :param start:
    :param end:
    :return: list containing the date-dicts
    """
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    valid_time = times[0].split(":")
    if len(valid_time) != 3:
        raise Exception(f"Invalid time format {times[0]} please use hh:mm:ss")

    _time_chunks = []
    for delta in range((end_date - start_date).days + 1):  # iterate over the date range to create a dict for each day in our time_chunks list. Later we can loop over those list entries to loop over the days
        i_date = start_date + timedelta(days=delta)

        if i_date > datetime.now(): # assignment description tells us to stop at the current date or the specified end date. I interpret that as "whatever is earlier"
            break

        i_date.replace(hour=int(valid_time[0]), minute=int(valid_time[1]), second=int(valid_time[2])) #set the timestamp to one of the time keys of the dataset for comparison with the zarr archive
        _time_chunks.append({
            "day": i_date.day,
            "month": i_date.month,
            "year": i_date.year,
            "string": i_date.strftime("%Y-%m-%d"),
            "timestamp": np.datetime64(i_date)
        })
    return _time_chunks


def calculate_healpix_grid(_nside: int) -> dict:
    """
    Calculates the positions of healpix pixels for a healpix grid with the given resolution. Returns the positions as
    latitude and longitude arrays. Also returns a name for later processing
    :param _nside: healpix resolution
    :return: dict{"latitude": np.ndarray, "longitude": np.ndarray, "name": nside resolution}
    """
    n_pix = hp.nside2npix(_nside)  # calculate number of pixels
    theta, phi = hp.pix2ang(_nside, np.arange(n_pix))  # calculate the pixel centers for each pixel in rad

    hp_latitude = 90 - np.degrees(theta)  # convert to degrees (North Pole = 0, South Pole = 180) and subtract from 90 to get to (North Pole = 90, South Pole = -90)
    hp_longitude = np.degrees(phi)
    return {"latitude": hp_latitude, "longitude": hp_longitude, "name": f'nside-{_nside}'}


def download_save_and_open_chunk(output_file: str, client: cdsapi.Client, day: int, month: int, year: int) -> xr.Dataset:
    """
    Downloads data according to the config and user input from the CDS-API. The downloaded data is stored in a file, opened and returned
    Before downloading the methode checks if the file has already been downloaded and is in good shape. In this case the file is just opened
    and returned
    :param output_file: path to storage file
    :param client: cdsapi.Client that should be used
    :param day: day to download
    :param month: month to download
    :param year: year to download
    :return:
    Dataset containing the data specified by user input and config
    """
    if Path(output_file).exists(): #check if file is already there
        print(f'{file_name + data_format["file_ending"]} was already downloaded. Checking file...', end=' ')
        try:
            dataset = xr.open_dataset(output_file) # try to open the file and return the content. If this doesn't work continue to download
            print(f'The file is in good shape. Continuing without download...')
            return dataset
        except:
            print(f'The file appears to be corrupted. Overwriting...')
    print(f"Downloading {file_name + data_format["file_ending"]}...")
    client.retrieve(collection, { #All the variable except the date are set in the config
        "product_type": product_type,
        "variable": variables,
        "year": year,
        "month": month,
        "day": day,
        "time": times,
        "pressure_level": pressure_levels,
        "grid": grid_res,
        "area": spacial_extend,
        "data_format": data_format["format"],
    }, output_file)
    print(f"Download completed")
    return xr.open_dataset(output_file)


def interpolate_and_clean_dataset(dataset: xr.Dataset, grid: dict) -> xr.Dataset:
    """
    Interpolates a dataset onto a grid.
    :param dataset: dataset to transform
    :param grid: dict{"latitude": np.ndarray, "longitude": np.ndarray}
    :return: transformed dataset
    """
    ds_interp = dataset.interp(
        latitude=xr.DataArray(grid["latitude"], dims='pix'),
        longitude=xr.DataArray(grid["longitude"], dims='pix'),
        method=interpolation_method
    )

    ds_interp = ds_interp.rename({"valid_time": 'time', "pressure_level": 'level'})  # rename to be more tsar_standard
    ds_interp = ds_interp.assign_coords(pix=("pix", np.arange(ds_interp.sizes["pix"], dtype=np.int64)))
    ds_interp = ds_interp.assign_coords(level=ds_interp["level"].astype(np.int32))
    ds_interp = ds_interp.drop_vars(["expver", "number"], errors="ignore")  # drop unnecessary variables

    return ds_interp


def required_action(zarr_ref: zarr.Group | None, group: str, timestamp: np.datetime64) -> str | None:
    """
    analyses the given zarr archive and determine what action is required for the group / timestamp combination.
    If the group or the whole archive doesn't exist, we have to choose the 'write' action to create the archive or at least the group.
    If the group exists but the timestamp isn't set, this day hasn't been stored in the archive and we have to append.
    If the timestamp has already been stored we have to do nothing
    :param zarr_ref: zarr.Group object, used to access the zarr archive
    :param group: name of the zarr group that is being processed
    :param timestamp: timestamp that is being processed
    :return: 'write', 'append' or None
    """
    ds_existing = None
    if zarr_ref is not None and group in zarr_ref.group_keys():
        ds_existing = xr.open_zarr(zarr_path, group=group_path)

    dimension_exists = (ds_existing is not None
                        and zarr_append_dim in ds_existing.dims
                        and ds_existing.sizes[zarr_append_dim] > 0)

    if dimension_exists and timestamp in ds_existing[zarr_append_dim].to_index():
        return None
    if dimension_exists:
        return 'append'
    return 'write'


def pix_to_grid_interp(da_pix, lat_name="latitude", lon_name="longitude", nlat=360, nlon=720) -> xr.DataArray:
    """
    Linearly interpolates regular grid from the healpix data
    :param da_pix: dataarray containing pixels
    :param lat_name: identifier for the latitude inside the array
    :param lon_name: identifier for the longitude inside the array
    :param nlat: lat resolution of the grid that gets created
    :param nlon: lon resolution of the grid that gets created
    :return: DataArray containing the regular grid, filled with the interpolated data
    """
    lats = da_pix[lat_name].values
    lons = da_pix[lon_name].values
    lons = ((lons + 180) % 360) - 180

    points = np.column_stack([lons, lats])
    values = da_pix.values

    lon_grid = np.linspace(-180, 180, nlon)
    lat_grid = np.linspace(-90, 90, nlat)
    lon2d, lat2d = np.meshgrid(lon_grid, lat_grid)

    out = griddata(
        points,
        values,
        (lon2d, lat2d),
        method="linear"
    )

    return xr.DataArray(
        out,
        dims=("lat", "lon"),
        coords={"lat": lat_grid, "lon": lon_grid},
        name=da_pix.name
    )


def plot_comparison(data_arrays, names, title) -> None:
    """
    methode to plot a comparison between multiple datarray grids in map representation
    :param data_arrays:
    :param names:
    :param title:
    :return:
    """

    # Create the plot with Robinson projection
    fig, ax = plt.subplots(ncols=3, figsize=(22, 6), subplot_kw={"projection": ccrs.Robinson()})

    mappable = None

    for i in range(len(data_arrays)):
        # Plot the temperature field
        mappable = data_arrays[i].plot(
            ax=ax[i],
            transform=ccrs.PlateCarree(),  # Data is in PlateCarree (lon/lat)
            cmap='coolwarm',
            add_colorbar=False,
            add_labels=False  # Avoid duplicate labels
        )

        # Add coastlines and country borders
        ax[i].add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax[i].add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':')
        ax[i].add_feature(cfeature.LAND, color='lightgray')
        ax[i].add_feature(cfeature.OCEAN, color='lightblue')
        ax[i].set_title(names[i])

        # add one colorbar for all plots
    cbar = fig.colorbar(
        mappable,
        ax=ax,
        orientation="vertical",
        fraction=0.035,  # thinner bar
        pad=0.06,  # <-- key: push it away from the plots
        shrink=0.9
    )
    cbar.set_label("Specific humidity (kg / kg)")
    fig.suptitle(title, fontsize=16, y=.9)
    plt.show()


def plot_two_samples(_time_chunks, _hp_grids):
    """
    methode to plot the first and the last timestamp that was just downloaded
    compares all available healpix grids and the original data
    :return:
    """
    display_times = [
        {
            "file_name": f'{collection_short_name}_{_time_chunks[0]["string"]}',
            "timestamp": f'{_time_chunks[0]["string"]}T{times[0]}'
        },
        {
            "file_name": f'{collection_short_name}_{time_chunks[-1]["string"]}',
            "timestamp": f'{_time_chunks[-1]["string"]}T{times[-1]}'
        }
    ]

    plt.ion() # needed so we can see multiple plots

    for display_time in display_times:
        _complete_path = storage_path + unprocessed_path + display_time["file_name"] + data_format["file_ending"]
        ds_unprocessed = xr.open_dataset(_complete_path)
        ds_processed_list = [xr.open_zarr(zarr_path, group=grid["name"]) for grid in _hp_grids]
        a_unprocessed = ds_unprocessed[plotting_variable_sn].sel(
            pressure_level=plotting_pressure_level,
            valid_time=display_time["timestamp"]
        )
        a_processed_list = [
            pix_to_grid_interp(ds_processed[plotting_variable_sn].sel(  #convert to regular grid
                level=plotting_pressure_level,
                time=display_time["timestamp"]
            ))
            for ds_processed
            in ds_processed_list
        ]

        plot_comparison(
            data_arrays=[a_unprocessed] + a_processed_list,
            names=['Original'] + [grid["name"] for grid in _hp_grids],
            title=f'Specific humidity at {plotting_pressure_level} hPa on {display_time["timestamp"]}'
        )
    input("Press Enter to exit") # needed so the interactive plot will stay open


if __name__ == '__main__':
    start, end = parse_user_input()
    print(f'Downloading and Processing {collection} over the range {start} -> {end}')

    setup()

    time_chunks = generate_time_chunks(default_temporal_extend['start'], default_temporal_extend['end'])

    hp_grids = [calculate_healpix_grid(nside) for nside in nsides]

    c = cdsapi.Client()

    zarr_path = storage_path + zarr_file

    for time_chunk in time_chunks:
        file_name = f'{collection_short_name}_{time_chunk["string"]}'
        complete_path = storage_path + unprocessed_path + file_name + data_format["file_ending"]

        ds = download_save_and_open_chunk(
            complete_path,
            c,
            time_chunk["day"],
            time_chunk["month"],
            time_chunk["year"]
        )

        ds = ds.sortby("latitude")

        zarr_root = zarr.open_group(zarr_path, mode="a") if Path(zarr_path).exists() else None  # Only read zarr_root once per processed day -> no unnecessary metadata reads

        for hp_grid in hp_grids:
            group_path = hp_grid["name"]

            action = required_action(zarr_root, group_path, time_chunk["timestamp"])

            if action is None:
                print(f'{file_name} in resolution {hp_grid["name"]} is already stored in archive. Skipping interpolation...')
                continue
            else:
                print(f"Interpolating {file_name} in resolution {hp_grid["name"]}")
                ds_hp = interpolate_and_clean_dataset(ds, hp_grid)

                if action == 'append':
                    print(f'Group {group_path} of archive {zarr_file} is not empty. Appending...')
                    ds_hp.to_zarr(zarr_path, group=group_path, mode="a", append_dim=zarr_append_dim)
                else:
                    print(f'Group {group_path} of archive {zarr_file} does not exists or is empty. Creating / Writing...')
                    ds_hp.to_zarr(zarr_path, group=group_path, mode="w")

        print(f'Processing of {collection_short_name}_{time_chunk["string"]} completed.')

    print(f'Downloading and Processing {collection} over the range {start} -> {end} completed.')
    plot_two_samples(time_chunks, hp_grids)



