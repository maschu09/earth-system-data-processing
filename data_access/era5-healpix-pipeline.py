from math import sin
import os
import logging
import xarray as xr
from era5_downloader import ERA5Downloader
from healpix_converter import create_healpix_dataset
from datetime import date, datetime, timedelta, timezone
from zarr_utils import save_healpix_to_zarr, append_to_zarr


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ERA5HealpixPipeline:
    def __init__(self, 
                 data_dir="./downloads/era5/healpix/", 
                 redownload=False,
                 single_zarr_file=True,
                 debug=False):
        self.data_dir = data_dir
        self.redownload = redownload    # if True, it will re-download existing data
        self.single_zarr_file = single_zarr_file  # if True, saves all data in a single Zarr file   
        self.debug = debug              # if True, it will not download actual data
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        self.downloader = ERA5Downloader()

    def process_and_archive_daily_data(
        self,
        start_date = date(1940, 1, 1),
        end_date = None,
        fixed_date = None       
    ):
        assert (start_date or end_date or fixed_date), "At least one of start_date, end_date, or fixed_date must be provided."
        assert not (end_date and fixed_date), "Provide either end_date or fixed_date, not both."

        start_date, end_date = self._get_start_and_end_dates(start_date, end_date, fixed_date)

        already_downloaded_dates = self._get_already_downloaded_dates()
        current_date = start_date
        while current_date <= end_date:
            if current_date in already_downloaded_dates and not self.redownload:
                print(f"Data for {current_date} already downloaded. Skipping.")
                current_date += timedelta(days=1)
                continue
            if not self.debug:
                nc_fpath = self.downloader.download_data_for_date(current_date)
                ds_hp8, ds_hp16 = self.process_lat_lon_data(nc_fpath)
                if self.single_zarr_file:
                    pass
                else:
                    ds_hp8.to_zarr(
                        os.path.join(self.data_dir, f"era5_healpix_nside8_{current_date.strftime('%Y-%m-%d')}.zarr"),
                        mode='w'
                    )
                    ds_hp16.to_zarr(
                        os.path.join(self.data_dir, f"era5_healpix_nside16_{current_date.strftime('%Y-%m-%d')}.zarr"),
                        mode='w'
                    )
                logger.info(f"Processed and saved HEALPix data for {current_date}")
                self.clean_up_temp_files(nc_fpath)
            current_date += timedelta(days=1)
        

    def _get_start_and_end_dates(self, start_date, end_date, fixed_date):
        latest_available_date = datetime.now(timezone.utc).date() - timedelta(days=5)

        if fixed_date:
            return fixed_date, fixed_date

        if start_date and end_date:
            return start_date, end_date

        if start_date and not end_date:
            return start_date, latest_available_date

        if end_date and not start_date:
            return date(1940, 1, 1), end_date
        
    def _get_already_downloaded_dates(self):
        already_downloaded_dates = []
        for fname in os.listdir(self.data_dir):
            if not os.path.isfile(os.path.join(self.data_dir, fname)): continue
            try:
                already_downloaded_dates.append(
                    datetime.strptime(fname.split('.')[0], "%Y-%m-%d").date()
                )
            except ValueError:
                continue
        return already_downloaded_dates

    def process_lat_lon_data(self, file_path):
        logger.info(f"Processing data from {file_path}...")
        ds_latlon = xr.open_dataset(file_path)
        ds_hp8 = create_healpix_dataset(ds_latlon, nside=8)
        ds_hp16 = create_healpix_dataset(ds_latlon, nside=16)
        return ds_hp8, ds_hp16

    def clean_up_temp_files(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {e}")

if __name__ == "__main__":
    pipeline = ERA5HealpixPipeline(debug=False,
        single_zarr_file=True)
    pipeline.process_and_archive_daily_data(
        start_date=date(2024,12,2),
        end_date=date(2024,12,3)
    )

