import os
import datetime
import argparse
import numpy as np
import healpy as hp
import xarray as xr
import cdsapi


def process_data(save_path: str, start_date: str = "1940-01-01", end_date: str = None, date: str = None,
                level_list: list = [975, 900, 800, 500, 300],
                param_list: list = ["133.128"],  # specific humidity
                param_shortname: str = "q",
                nside_list: list = [8, 16]
                    ):

    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    already_processed_dates = [f.replace(".zarr", "") for f in os.listdir(save_path)]
    
    if date is not None: # process single date
        dates_to_process = [date] if date not in already_processed_dates else []
    else:
        if end_date is None: # process until today
            end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        # check that start date is before end date
        assert start_dt <= end_dt, "Start date must be before end date"

        delta = end_dt - start_dt
        dates_to_process = [(start_dt + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
                            if (start_dt + datetime.timedelta(days=i)).strftime("%Y-%m-%d") not in already_processed_dates]

    c = cdsapi.Client()
    for d in dates_to_process:
        
        # fetch from cds api
        file_pth = os.path.join(save_path, f"{d}.nc")
        c.retrieve("reanalysis-era5-complete", {
        "class": "ea",
        "type": "an",  # analysis data
        "stream": "oper",
        "expver": "1",
        "levtype": "pl",
        "date": d,  # date in YYYY-MM-DD
        "time": "00:00:00/06:00:00/12:00:00/18:00:00",  # 6-hourly
        "levelist": "/".join([str(lv) for lv in level_list]),
        "param": "/".join(param_list),
        "grid": "5.625/5.625",
        "format": "netcdf"
        }, file_pth)

        # load data
        ds = xr.open_dataset(file_pth)

        ## transform to healpix
        maps = {nside: [] for nside in nside_list}
        times = []
        levels = []

        pressure_levels = ds.pressure_level.values
        time_steps = ds.valid_time.values
        for t in time_steps:
            for p in pressure_levels:

                selected_data = ds[param_shortname].sel(
                    valid_time=t,
                    pressure_level=p
                )
                data = selected_data.values
                lon = selected_data.longitude.values
                lat = selected_data.latitude.values

                lon_grid, lat_grid = np.meshgrid(lon, lat)
                theta = np.deg2rad(90 - lat_grid)  # Converts latitude to colatitude
                phi = np.deg2rad(lon_grid)

                for nside in nside_list:
                    pixel_indices = hp.ang2pix(nside, theta, phi)
                    m = np.zeros(hp.nside2npix(nside))
                    counts = np.zeros(hp.nside2npix(nside))

                    # accumulate data assigned to every possition and count occurrences
                    np.add.at(m, pixel_indices.ravel(), data.ravel())
                    np.add.at(counts, pixel_indices.ravel(), 1)

                    # average summed data by number of occurrences
                    mask = counts > 0
                    m[mask] /= counts[mask]

                    maps[nside].append(m)

                times.append(np.datetime64(t))
                levels.append(int(p))

        ## save as zarr
        zarr_path = os.path.join(save_path, f"{d}.zarr")
        for nside, data_list in maps.items(): # group by nside
            data = np.stack(data_list, axis=0) # stack pixmaps

            ds_hp = xr.Dataset(
                {
                    param_shortname: (("sample", "pix"), data)
                },
                coords={
                    "sample": np.arange(len(data_list)),
                    "time": ("sample", times),
                    "level": ("sample", levels),
                    "pix": np.arange(data.shape[1]),
                }
            )

            ds_hp = (
                ds_hp
                .set_index(sample=("time", "level"))
                .unstack("sample") # reshape to have time and level as dimensions
                .chunk(
                    {
                        "time": 1,
                        "level": 1,
                        "pix": -1 # all pixels in one chunk
                    }
                )
            )

            group = f"nside={nside}"
            mode = "w" if not os.path.exists(os.path.join(zarr_path, group)) else "a" # append if group exists
            ds_hp.to_zarr(
                zarr_path,
                group=group,
                mode=mode,
                append_dim="time" if mode == "a" else None # append along time dimension
            )

        ## remove temp file
        os.remove(file_pth)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--save_path', dest='save_path', type=str, help='Path to save data', required=True)
    parser.add_argument('--start_date', dest='start_date', type=str, help='Add start date', default="1940-01-01")
    parser.add_argument('--end_date', dest='end_date', type=str, help='Add end date', default=None)
    parser.add_argument('--date', dest='date', type=str, help='Add specific date', default=None)
    parser.add_argument("--levels", nargs="+", type=int, help="Pressure levels", default=[975, 900, 800, 500, 300])
    parser.add_argument("--params", nargs="+", type=str, help="Parameter codes", default=["133.128"])  # specific humidity
    parser.add_argument("--shortname", type=str, help="Parameter shortname", default="q")
    parser.add_argument("--nsides", nargs="+", type=int, help="Healpix nside values", default=[8, 16])

    args = parser.parse_args()

    process_data(save_path=args.save_path,
                 start_date=args.start_date,
                 end_date=args.end_date,
                 date=args.date,
                 level_list=args.levels,
                 param_list=args.params,
                 param_shortname=args.shortname,
                 nside_list=args.nsides
                 )