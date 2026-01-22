import os
import cdsapi
import shutil
import logging
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ERA5Downloader:
    def __init__(self, config=None, data_dir="./downloads/era5/netcdf/"):
        """
        Docstring for __init__
        
        :param config: (dict, optional) Configuration dictionary with keys:
            - variables (list): ERA5 variable names to download
            - pressure_levels (list): Pressure levels in hPa
            - times (list): Times in HH:MM format (24h)
            - area (list): [North, West, South, East] in degrees
            Default uses predefined standard configuration if not provided
        """
        if config is None:
            self.config = self._get_default_download_config()
        else:
            self.config = config
        # Validate config
        try:
            self.config = self._validate_download_config(self.config)
        except ValueError as e:
            logger.error(f"Invalid configuration: {e}")
        self.data_dir = data_dir
        self.client = cdsapi.Client()
        
    def download_data_for_date(self, target_date):
        """
        Download ERA5 reanalysis data for a specific date.
        
        Args:
            target_date (date): The date to download data for
        
        Returns:
            str or None: Path to downloaded file if successful, None if failed or debug mode
        """        
        logger.info(f"Starting download for {target_date}")
        
        # Create temporary directory for downloads
        temp_dir = None
        try:
            temp_dir = tempfile.mkdtemp(
                prefix="era5_download_",
                dir=self.data_dir
            )
            logger.debug(f"Created temporary directory: {temp_dir}")
            
            # Prepare request parameters
            request_params = self._build_cds_request(target_date, self.config)
            
            # Download file
            output_file = os.path.join(temp_dir, f"{target_date.strftime('%Y-%m-%d')}.nc")
            logger.debug(f"Downloading to: {output_file}")
            
            self.client.retrieve(
                'reanalysis-era5-pressure-levels',
                request_params,
                output_file
            )
            
            # Verify file exists and has content
            if not os.path.exists(output_file):
                logger.error(f"Download completed but file not found: {output_file}")
                return None
            
            file_size = os.path.getsize(output_file)
            if file_size == 0:
                logger.error(f"Downloaded file is empty: {output_file}")
                return None
            
            logger.info(f"Successfully downloaded {file_size / 1024 / 1024:.2f} MB for {target_date}")
            
            # Move file from temp directory to data directory
            final_path = os.path.join(self.data_dir, f"{target_date.strftime('%Y-%m-%d')}.nc")
            shutil.move(output_file, final_path)
            logger.debug(f"Moved file to: {final_path}")
            
            return final_path
            
        except Exception as e:
            logger.error(f"Download failed for {target_date}: {type(e).__name__}: {e}")
            return None
        
        finally:
            # Clean up temporary directory if it still exists
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temporary directory: {temp_dir}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")
    
    def _get_default_download_config(self):
        """Returns the default download configuration."""
        return {
            "variable": [
                "relative_humidity",
                "specific_humidity"
            ],
            "pressure_level": [
                "300", "500", "800",
                "900", "975"
            ],
            "time": ["00:00", "06:00", "12:00", "18:00"],
            "area": [90, -180, -90, 180],  # Global coverage
        }
    
    def _validate_download_config(self, config):
        """
        Validate download configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        required_keys = {"variable", "pressure_level", "time"}
        provided_keys = set(config.keys())
        
        if not required_keys.issubset(provided_keys):
            missing = required_keys - provided_keys
            raise ValueError(f"Missing required config keys: {missing}")
        
        if not isinstance(config["variable"], list) or len(config["variable"]) == 0:
            raise ValueError("variable must be a non-empty list")
        
        if not isinstance(config["pressure_level"], list) or len(config["pressure_level"]) == 0:
            raise ValueError("pressure_level must be a non-empty list")
        
        if not isinstance(config["time"], list) or len(config["time"]) == 0:
            raise ValueError("time must be a non-empty list")
        
        if not config.get("area", False):
            config["area"] = [90, -180, -90, 180]  # Default to global coverage
        if not isinstance(config["area"], list) or len(config["area"]) != 4:
            raise ValueError("area must be a list of 4 values [North, West, South, East]")
        
        return config
    
    def _build_cds_request(self, target_date, config):
        """
        Build CDS API request parameters from configuration and date.
        
        Args:
            target_date (date): Target date for download
            config (dict): Download configuration
        
        Returns:
            dict: CDS API request parameters
        """
        return {
            "product_type": "reanalysis",
            "format": "netcdf",
            "variable": config["variable"],
            "pressure_level": config["pressure_level"],
            "year": str(target_date.year),
            "month": f"{target_date.month:02d}",
            "day": f"{target_date.day:02d}",
            "time": config["time"],
            "area": config["area"],
        }