"""
Main control flow script for ERA5 data pipeline.
Handles downloading, processing, and archiving with date-based workflow.

Usage:
    # Process all missing files from start date to current date
    python era5_pipeline.py
    
    # Process a specific date
    python era5_pipeline.py 2024-12-01
    
    # Process from specific date to end date
    python era5_pipeline.py --start 2024-12-01 --end 2024-12-05
    
    # Mock processing (no download)
    python era5_pipeline.py --mock
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from config import (
    ERA5_CONFIG,
    DATA_DIR,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    LOG_DIR,
)
from download import download_era5_daily, find_oldest_missing_file
from processing import process_and_archive

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_single_date(
    date: datetime,
    mock: bool = False,
    variable: str = ERA5_CONFIG["variable"],
) -> bool:
    """
    Process a single date through the entire pipeline.
    
    Parameters
    ----------
    date : datetime
        Date to process
    mock : bool
        If True, skip actual download and use mock processing
    variable : str
        Variable name
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    date_str = date.strftime('%Y-%m-%d')
    logger.info(f"{'[MOCK] ' if mock else ''}Processing date: {date_str}")
    
    try:
        if not mock:
            # Step 1: Download
            logger.info(f"Step 1/3: Downloading ERA5 data for {date_str}")
            input_file = download_era5_daily(
                date=date,
                variable=variable,
                pressure_levels=ERA5_CONFIG["pressure_levels"],
                times=ERA5_CONFIG["times"],
                output_format=ERA5_CONFIG["format"],
                grid=ERA5_CONFIG["grid"],
            )
            
            if input_file is None:
                logger.error(f"Download failed for {date_str}")
                return False
        else:
            # Create mock input file
            date_str_file = date.strftime("%Y%m%d")
            ext = "nc" if ERA5_CONFIG["format"] == "netcdf" else "grib"
            input_file = DATA_DIR / f"era5_{variable}_{date_str_file}.{ext}"
            
            # Create mock file
            input_file.parent.mkdir(parents=True, exist_ok=True)
            input_file.touch()
            logger.info(f"[MOCK] Created mock input file: {input_file}")
        
        # Step 2: Process and Archive
        logger.info(f"Step 2/3: Processing data for {date_str}")
        success = process_and_archive(input_file)
        
        if not success:
            logger.error(f"Processing failed for {date_str}")
            return False
        
        logger.info(f"✓ Successfully completed all steps for {date_str}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {date_str}: {str(e)}")
        return False


def process_date_range(
    start_date: datetime,
    end_date: datetime,
    mock: bool = False,
    variable: str = ERA5_CONFIG["variable"],
) -> tuple[int, int]:
    """
    Process all dates in a range.
    
    Parameters
    ----------
    start_date : datetime
        Start of date range
    end_date : datetime
        End of date range
    mock : bool
        If True, skip actual download and use mock processing
    variable : str
        Variable name
    
    Returns
    -------
    tuple[int, int]
        (successful_count, failed_count)
    """
    successful = 0
    failed = 0
    current_date = start_date
    
    total_days = (end_date - start_date).days + 1
    logger.info(f"Processing {total_days} days from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    while current_date <= end_date:
        if process_single_date(current_date, mock=mock, variable=variable):
            successful += 1
        else:
            failed += 1
        current_date += timedelta(days=1)
    
    return successful, failed


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="ERA5 data download, processing, and archiving pipeline"
    )
    
    parser.add_argument(
        "date",
        nargs="?",
        help="Specific date to process (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--start",
        type=str,
        help="Start date (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end",
        type=str,
        help="End date (format: YYYY-MM-DD)"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with mock processing (no actual download)"
    )
    parser.add_argument(
        "--find-missing",
        action="store_true",
        help="Find oldest missing file and process from there"
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 70)
    logger.info("ERA5 Pipeline Started")
    logger.info("=" * 70)
    
    try:
        start_date = DEFAULT_START_DATE
        end_date = DEFAULT_END_DATE
        
        # Parse arguments
        if args.date:
            # Process single date
            single_date = datetime.strptime(args.date, "%Y-%m-%d")
            start_date = single_date
            end_date = single_date
            logger.info(f"Mode: Single date processing ({args.date})")
        
        elif args.start or args.end:
            # Process date range
            if args.start:
                start_date = datetime.strptime(args.start, "%Y-%m-%d")
            if args.end:
                end_date = datetime.strptime(args.end, "%Y-%m-%d")
            logger.info(f"Mode: Date range processing ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})")
        
        elif args.find_missing:
            # Find oldest missing file and process from there
            oldest_missing = find_oldest_missing_file(
                DEFAULT_START_DATE,
                DEFAULT_END_DATE,
                DATA_DIR,
                ERA5_CONFIG["variable"]
            )
            
            if oldest_missing is None:
                logger.info("All files in default date range already exist")
                end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                start_date = oldest_missing
                logger.info(f"Mode: Processing from oldest missing file ({start_date.strftime('%Y-%m-%d')})")
        
        else:
            # Default: find oldest missing file
            oldest_missing = find_oldest_missing_file(
                DEFAULT_START_DATE,
                DEFAULT_END_DATE,
                DATA_DIR,
                ERA5_CONFIG["variable"]
            )
            
            if oldest_missing is None:
                logger.info("All files already exist, no processing needed")
                logger.info("=" * 70)
                logger.info("ERA5 Pipeline Completed")
                logger.info("=" * 70)
                return 0
            
            start_date = oldest_missing
            logger.info(f"Mode: Default (processing from oldest missing: {start_date.strftime('%Y-%m-%d')})")
        
        # Set end date to today if not specified
        if end_date < datetime.now():
            end_date = min(end_date, datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        
        if args.mock:
            logger.info("*** MOCK MODE - No actual data will be downloaded ***")
        
        # Process dates
        successful, failed = process_date_range(
            start_date,
            end_date,
            mock=args.mock,
            variable=ERA5_CONFIG["variable"]
        )
        
        # Log summary
        logger.info("=" * 70)
        logger.info("ERA5 Pipeline Completed")
        logger.info(f"Successful: {successful}, Failed: {failed}")
        logger.info("=" * 70)
        
        return 0 if failed == 0 else 1
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}", exc_info=True)
        logger.info("=" * 70)
        logger.info("ERA5 Pipeline Failed")
        logger.info("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
