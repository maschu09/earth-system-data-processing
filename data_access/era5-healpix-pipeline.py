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
                 data_dir="./downloads/era5/", 
                 redownload=False,
                 single_zarr_file=True,
                 debug=False):
        self.healpix_dir = os.path.join(data_dir, "healpix/")
        self.netcdf_dir = os.path.join(data_dir, "netcdf/")
        self.redownload = redownload    # if True, it will re-download existing data
        self.single_zarr_file = single_zarr_file  # if True, saves all data in a single Zarr file   
        self.debug = debug              # if True, it will not download actual data
        if not os.path.exists(self.healpix_dir):
            os.makedirs(self.healpix_dir)
        if not os.path.exists(self.netcdf_dir):
            os.makedirs(self.netcdf_dir)
        self.downloader = ERA5Downloader(data_dir=self.netcdf_dir)
        
        # Zarr file paths for single output mode
        self.zarr_nside8_path = os.path.join(self.healpix_dir, "era5_healpix_nside8_consolidated.zarr")
        self.zarr_nside16_path = os.path.join(self.healpix_dir, "era5_healpix_nside16_consolidated.zarr")
        self._zarr_initialized = False

    def process_and_archive_daily_data(
        self,
        start_date = date(1940, 1, 1),
        end_date = None,
        fixed_date = None       
    ):
        assert (start_date or end_date or fixed_date), "At least one of start_date, end_date, or fixed_date must be provided."
        assert not (end_date and fixed_date), "Provide either end_date or fixed_date, not both."

        start_date, end_date = self._get_start_and_end_dates(start_date, end_date, fixed_date)
        
        # Reset zarr initialization flag for new pipeline run
        self._zarr_initialized = False

        already_downloaded_dates = self._get_already_downloaded_dates()
        current_date = start_date
        while current_date <= end_date:
            if current_date in already_downloaded_dates and not self.redownload:
                print(f"Data for {current_date} already downloaded. Skipping.")
                nc_fpath = os.path.join(self.netcdf_dir, f"{current_date.strftime('%Y-%m-%d')}.nc")
            elif not self.debug:
                nc_fpath = self.downloader.download_data_for_date(current_date)
            else:
                logger.info(f"Debug mode: Skipping download and processing for {current_date}")
                current_date += timedelta(days=1)
                continue
            ds_hp8, ds_hp16 = self.process_lat_lon_data(nc_fpath)
            print(f"ds_hp8 shape: {ds_hp8.dims}")
            print(f"ds_hp8 time length: {len(ds_hp8.time)}")
            print(f"ds_hp8 data vars: {list(ds_hp8.data_vars)}")
            if self.single_zarr_file:
                self._save_to_consolidated_zarr(ds_hp8, ds_hp16)
            else:
                ds_hp8.to_zarr(
                    os.path.join(self.healpix_dir, f"era5_healpix_nside8_{current_date.strftime('%Y-%m-%d')}.zarr"),
                    mode='w'
                )
                ds_hp16.to_zarr(
                    os.path.join(self.healpix_dir, f"era5_healpix_nside16_{current_date.strftime('%Y-%m-%d')}.zarr"),
                    mode='w'
                )
            logger.info(f"Processed and saved HEALPix data for {current_date}")
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
        for fname in os.listdir(self.netcdf_dir):
            if not os.path.isfile(os.path.join(self.netcdf_dir, fname)): continue
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
    
    def _save_to_consolidated_zarr(self, ds_hp8, ds_hp16):
        """
        Save HEALPix datasets to consolidated zarr files.
        Creates files on first call, appends on subsequent calls.
        
        Parameters:
        -----------
        ds_hp8 : xr.Dataset
            HEALPix dataset with nside=8
        ds_hp16 : xr.Dataset
            HEALPix dataset with nside=16
        """
        try:
            if not self._zarr_initialized:
                # First iteration: create new zarr files
                logger.info(f"Creating consolidated zarr files")
                save_healpix_to_zarr(ds_hp8, nside=8, output_path=self.zarr_nside8_path, mode='w')
                save_healpix_to_zarr(ds_hp16, nside=16, output_path=self.zarr_nside16_path, mode='w')
                self._zarr_initialized = True
                logger.info(f"Initialized zarr files at {self.zarr_nside8_path} and {self.zarr_nside16_path}")
            else:
                # Subsequent iterations: append to existing zarr files
                logger.debug(f"Appending to existing zarr files")
                append_to_zarr(ds_hp8, self.zarr_nside8_path)
                append_to_zarr(ds_hp16, self.zarr_nside16_path)
                logger.debug(f"Successfully appended data to zarr stores")
        except Exception as e:
            logger.error(f"Error saving to consolidated zarr: {type(e).__name__}: {e}")
            raise

if __name__ == "__main__":
    pipeline = ERA5HealpixPipeline(debug=True, single_zarr_file=True)
    pipeline.process_and_archive_daily_data(
        start_date=date(2024,12,1),
        end_date=date(2024,12,5)
    )

