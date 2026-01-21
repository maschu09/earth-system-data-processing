"""
plot-with-zarr.py

Intended plotting script for Homework 2.

This script:
- loads two arbitrary time samples from the Zarr store,
- plots the stored original lat–lon data,
- plots the stored HEALPix data for NSIDE=8 and NSIDE=16.

Note:
Reopening Zarr stores via xarray may fail on some platforms
(e.g. Windows + Zarr v3). The logic is implemented as intended
by the homework specification and documented accordingly.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import xarray as xr

from config import ZARR_DIR, NSIDE_VALUES, PLOTS_DIR


def main():
    # --------------------------------------------------
    # Open Zarr store
    # --------------------------------------------------
    zarr_path = ZARR_DIR / "era5_specific_humidity_healpix.zarr"

    if not zarr_path.exists():
        raise FileNotFoundError(f"Zarr store not found: {zarr_path}")

    try:
        ds = xr.open_zarr(zarr_path)
    except Exception as e:
        raise RuntimeError(
            "Failed to open Zarr store with xarray. "
            "This is a known platform-specific limitation."
        ) from e

    # --------------------------------------------------
    # Select two arbitrary time samples
    # --------------------------------------------------
    if ds.time.size < 2:
        raise ValueError("Zarr store contains fewer than two time samples.")

    times = [
        ds.time.values[0],
        ds.time.values[1],
    ]

    # --------------------------------------------------
    # Plot data for each selected time
    # --------------------------------------------------
    for t in times:
        date_str = str(t)[:10]

        # -------------------------------
        # Plot original lat–lon data
        # -------------------------------
        da_ll = ds["specific_humidity_latlon"].sel(time=t)

        plt.figure(figsize=(8, 4))
        da_ll.plot()
        plt.title(f"ERA5 specific humidity (lat–lon)\n{date_str}")
        plt.tight_layout()

        out_ll = PLOTS_DIR / f"era5_latlon_{date_str}.png"
        plt.savefig(out_ll, dpi=150)
        plt.close()

        # -------------------------------
        # Plot HEALPix data
        # -------------------------------
        for nside in NSIDE_VALUES:
            da_hp = ds["specific_humidity_healpix"].sel(
                time=t,
                nside=nside,
            )

            healpix_index = da_hp["healpix"].values
            values = da_hp.values

            plt.figure(figsize=(8, 4))
            plt.scatter(
                healpix_index,
                values,
                s=4,
            )
            plt.xlabel("HEALPix pixel index")
            plt.ylabel("Specific humidity (kg/kg)")
            plt.title(f"HEALPix NSIDE={nside}\n{date_str}")
            plt.tight_layout()

            out_hp = PLOTS_DIR / f"healpix_nside{nside}_{date_str}.png"
            plt.savefig(out_hp, dpi=150)
            plt.close()


if __name__ == "__main__":
    main()
