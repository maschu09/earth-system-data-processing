"""
Plotting script for Homework 2

Usage:
    python src/plot.py YYYY-MM-DD

This script:
1. Plots ERA5 lat-lon data
2. Converts ERA5 to HEALPix (NSIDE 8 & 16) and plots
3. Attempts to load and plot HEALPix data from Zarr (if readable)
"""

import sys
from pathlib import Path

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from astropy_healpix import HEALPix
import astropy.units as u

from config import RAW_DATA_DIR, ZARR_DIR, PLOTS_DIR, NSIDE_VALUES


def plot_for_day(date_str: str):

    # --------------------------------------------------
    # 1. Load ERA5 NetCDF
    # --------------------------------------------------
    era5_file = RAW_DATA_DIR / f"era5_{date_str.replace('-', '')}.nc"
    if not era5_file.exists():
        raise FileNotFoundError(f"ERA5 file not found: {era5_file}")

    ds = xr.open_dataset(era5_file)

    da = (
        ds["q"]
        .sel(pressure_level=800)
        .isel(valid_time=0)
    )

    lats = da["latitude"].values
    lons = da["longitude"].values
    values = da.values

    # --------------------------------------------------
    # 2. Plot ERA5 lat–lon field
    # --------------------------------------------------
    plt.figure(figsize=(10, 4))
    da.plot(cmap="viridis", cbar_kwargs={"label": "Specific humidity (kg/kg)"})
    plt.title(f"ERA5 specific humidity (800 hPa)\n{date_str}")
    plt.tight_layout()

    plt.savefig(PLOTS_DIR / f"era5_latlon_800hpa_{date_str}.png", dpi=150)
    plt.close()

    # --------------------------------------------------
    # 3. ERA5 → HEALPix conversion + plotting
    # --------------------------------------------------
    lon2d, lat2d = np.meshgrid(lons, lats)
    lon_flat = lon2d.ravel()
    lat_flat = lat2d.ravel()
    val_flat = values.ravel()

    for nside in NSIDE_VALUES:
        hp = HEALPix(nside=nside, order="nested", frame="icrs")

        pix = hp.lonlat_to_healpix(
            lon_flat * u.deg,
            lat_flat * u.deg
        )

        npix = hp.npix
        hp_map = np.full(npix, np.nan)

        for p in range(npix):
            mask = pix == p
            if np.any(mask):
                hp_map[p] = np.nanmean(val_flat[mask])

        plt.figure(figsize=(8, 4))
        plt.scatter(
            np.arange(npix),
            hp_map,
            s=4
        )
        plt.xlabel("HEALPix pixel index")
        plt.ylabel("Specific humidity (kg/kg)")
        plt.title(f"HEALPix from ERA5 (NSIDE={nside})\n{date_str}")
        plt.tight_layout()

        plt.savefig(
            PLOTS_DIR / f"healpix_from_era5_nside{nside}_{date_str}.png",
            dpi=150
        )
        plt.close()

    # --------------------------------------------------
    # 4. Attempt to load & plot from Zarr (optional)
    # --------------------------------------------------
    zarr_store = ZARR_DIR / f"era5_healpix_{date_str}.zarr"

    if zarr_store.exists():
        try:
            ds_hp = xr.open_zarr(zarr_store)

            for nside in NSIDE_VALUES:
                da_hp = ds_hp["specific_humidity"].sel(nside=nside)

                plt.figure(figsize=(8, 4))
                plt.scatter(
                    da_hp["healpix"].values,
                    da_hp.values,
                    s=4
                )
                plt.xlabel("HEALPix pixel index")
                plt.ylabel("Specific humidity (kg/kg)")
                plt.title(f"HEALPix from Zarr (NSIDE={nside})\n{date_str}")
                plt.tight_layout()

                plt.savefig(
                    PLOTS_DIR / f"healpix_from_zarr_nside{nside}_{date_str}.png",
                    dpi=150
                )
                plt.close()

        except Exception as e:
            print("Zarr plotting skipped due to read error:")
            print(e)

    else:
        print("Zarr store not found - skipping Zarr plots.")


def main():
    if len(sys.argv) != 2:
        print("Usage: python src/plot.py YYYY-MM-DD")
        sys.exit(1)

    date_str = sys.argv[1]
    plot_for_day(date_str)
    print(f"Plots saved to {PLOTS_DIR}")


if __name__ == "__main__":
    main()
