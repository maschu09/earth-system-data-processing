"""
Data processing module for ERA5 files.
Handles processing and archiving of downloaded data.
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import PROCESSED_DIR, ARCHIVE_DIR, LOG_DIR

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def process_daily_data(
    input_file: Path,
    output_dir: Path = PROCESSED_DIR,
) -> Optional[Path]:
    """
    Process daily ERA5 data file.
    
    Parameters
    ----------
    input_file : Path
        Path to input file (downloaded from ERA5)
    output_dir : Path
        Directory to save processed file
    
    Returns
    -------
    Optional[Path]
        Path to processed file if successful, None otherwise
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return None
    
    try:
        # Construct output filename
        output_filename = f"processed_{input_file.name}"
        output_path = output_dir / output_filename
        
        logger.info(f"Processing file: {input_file.name}")
        
        # TODO: Add actual processing logic here
        # For now, just copy the file as a placeholder
        # In reality, this might involve:
        # - Regridding
        # - Unit conversions
        # - Quality checks
        # - Merging with other data
        
        shutil.copy2(input_file, output_path)
        
        logger.info(f"Successfully processed to: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Failed to process {input_file.name}: {str(e)}")
        return None


def archive_file(
    file_path: Path,
    archive_dir: Path = ARCHIVE_DIR,
) -> Optional[Path]:
    """
    Archive processed file.
    
    Parameters
    ----------
    file_path : Path
        Path to file to archive
    archive_dir : Path
        Directory to move file to
    
    Returns
    -------
    Optional[Path]
        Path to archived file if successful, None otherwise
    """
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return None
    
    try:
        # Create archive subdirectory by date
        date_subdir = archive_dir / file_path.name.split('_')[2][:4] / file_path.name.split('_')[2][4:6]
        date_subdir.mkdir(parents=True, exist_ok=True)
        
        archived_path = date_subdir / file_path.name
        shutil.move(str(file_path), str(archived_path))
        
        logger.info(f"Archived file to: {archived_path}")
        return archived_path
        
    except Exception as e:
        logger.error(f"Failed to archive {file_path.name}: {str(e)}")
        return None


def process_and_archive(
    input_file: Path,
    processed_dir: Path = PROCESSED_DIR,
    archive_dir: Path = ARCHIVE_DIR,
) -> bool:
    """
    Process and archive a file in a single step.
    
    Parameters
    ----------
    input_file : Path
        Path to input file
    processed_dir : Path
        Directory for processed files
    archive_dir : Path
        Directory for archived files
    
    Returns
    -------
    bool
        True if successful, False otherwise
    """
    # Process the file
    processed_file = process_daily_data(input_file, processed_dir)
    
    if processed_file is None:
        return False
    
    # Archive the processed file
    archived_file = archive_file(processed_file, archive_dir)
    
    if archived_file is None:
        return False
    
    logger.info(f"Successfully completed processing and archiving for {input_file.name}")
    return True
