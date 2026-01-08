"""
ERA5 data download module.
Flexible download routine that can be adapted to different variables and pressure levels.
"""

import cdsapi
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from config import ERA5_CONFIG, DATA_DIR, LOG_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def download_era5_daily(
    date: datetime,
    variable: str = ERA5_CONFIG["variable"],
    pressure_levels: List[int] = ERA5_CONFIG["pressure_levels"],
    times: List[str] = ERA5_CONFIG["times"],
    output_format: str = ERA5_CONFIG["format"],
    grid: Optional[List[float]] = ERA5_CONFIG["grid"],
    output_dir: Path = DATA_DIR,
) -> Optional[Path]:
    """
    Download ERA5 data for a single day.
    
    Parameters
    ----------
    date : datetime
        The date for which to download data
    variable : str
        Variable name (e.g., 'relative_humidity')
    pressure_levels : List[int]
        List of pressure levels in hPa
    times : List[str]
        List of times in HH:MM format (6-hourly: 00:00, 06:00, 12:00, 18:00)
    output_format : str
        Output format ('netcdf' or 'grib')
    grid : Optional[List[float]]
        Grid resolution [lat, lon]. None uses original resolution.
    output_dir : Path
        Directory to save downloaded files
    
    Returns
    -------
    Optional[Path]
        Path to downloaded file if successful, None otherwise
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Format filename
    date_str = date.strftime("%Y%m%d")
    ext = "nc" if output_format == "netcdf" else "grib"
    output_filename = f"era5_{variable}_{date_str}.{ext}"
    output_path = output_dir / output_filename
    
    # Skip if file already exists
    if output_path.exists():
        logger.info(f"File already exists: {output_path}")
        return output_path
    
    try:
        client = cdsapi.Client()
        
        logger.info(f"Downloading ERA5 data for {date.strftime('%Y-%m-%d')}")
        logger.info(f"Variable: {variable}, Pressure levels: {pressure_levels}")
        
        # Build request
        request = {
            'product_type': 'reanalysis',
            'format': output_format,
            'variable': variable,
            'pressure_level': pressure_levels,
            'date': date.strftime('%Y-%m-%d'),
            'time': times,
        }
        
        # Add grid if specified
        if grid is not None:
            request['grid'] = grid
        
        # Download
        client.retrieve('reanalysis-era5-pressure-levels', request, str(output_path))
        
        logger.info(f"Successfully downloaded to: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to download data for {date_str}: {str(e)}")
        return None


def find_oldest_missing_file(
    start_date: datetime,
    end_date: datetime,
    data_dir: Path = DATA_DIR,
    variable: str = ERA5_CONFIG["variable"],
) -> Optional[datetime]:
    """
    Find the oldest missing file in the date range.
    
    Parameters
    ----------
    start_date : datetime
        Start of date range
    end_date : datetime
        End of date range
    data_dir : Path
        Directory containing downloaded files
    variable : str
        Variable name (to match filenames)
    
    Returns
    -------
    Optional[datetime]
        Datetime of oldest missing file, or None if all files exist
    """
    current_date = start_date
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y%m%d")
        # Check both possible formats
        nc_file = data_dir / f"era5_{variable}_{date_str}.nc"
        grib_file = data_dir / f"era5_{variable}_{date_str}.grib"
        
        if not nc_file.exists() and not grib_file.exists():
            logger.info(f"Missing file for date: {current_date.strftime('%Y-%m-%d')}")
            return current_date
        
        current_date += timedelta(days=1)
    
    return None
