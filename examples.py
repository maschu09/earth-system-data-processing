"""
Example: Using the ERA5 Pipeline Programmatically

This script demonstrates how to use the pipeline modules directly in your own code.
"""

from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add data_access to path for imports
sys.path.insert(0, str(Path(__file__).parent / "data_access"))

from config import ERA5_CONFIG, DEFAULT_START_DATE, DEFAULT_END_DATE
from download import download_era5_daily, find_oldest_missing_file
from processing import process_and_archive

def example_1_download_single_date():
    """Download ERA5 data for a single date."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Download data for a single date")
    print("="*70)
    
    date = datetime(2024, 12, 1)
    print(f"\nDownloading ERA5 {ERA5_CONFIG['variable']} for {date.strftime('%Y-%m-%d')}...")
    
    file_path = download_era5_daily(date)
    if file_path:
        print(f"✓ Downloaded to: {file_path}")
    else:
        print("✗ Download failed")


def example_2_download_with_custom_settings():
    """Download with custom variables and pressure levels."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Download with custom settings")
    print("="*70)
    
    date = datetime(2024, 12, 1)
    print(f"\nDownloading ERA5 temperature for {date.strftime('%Y-%m-%d')}...")
    print("Custom settings: pressure_levels=[850, 700, 500], format=netcdf")
    
    file_path = download_era5_daily(
        date=date,
        variable="temperature",
        pressure_levels=[850, 700, 500],
        times=["00:00", "06:00", "12:00", "18:00"],
        output_format="netcdf",
        grid=None  # Original resolution
    )
    if file_path:
        print(f"✓ Downloaded to: {file_path}")
    else:
        print("✗ Download failed")


def example_3_find_missing_files():
    """Find oldest missing file in date range."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Find oldest missing file")
    print("="*70)
    
    oldest_missing = find_oldest_missing_file(
        DEFAULT_START_DATE,
        DEFAULT_END_DATE,
        variable=ERA5_CONFIG["variable"]
    )
    
    if oldest_missing:
        print(f"\nOldest missing file: {oldest_missing.strftime('%Y-%m-%d')}")
    else:
        print("\nAll files in date range already exist!")


def example_4_process_date_range():
    """Download and process a date range."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Process date range")
    print("="*70)
    
    start_date = datetime(2024, 12, 1)
    end_date = datetime(2024, 12, 3)
    
    print(f"\nProcessing {(end_date - start_date).days + 1} days...")
    current_date = start_date
    successful = 0
    failed = 0
    
    while current_date <= end_date:
        print(f"\nProcessing {current_date.strftime('%Y-%m-%d')}...")
        
        # Download
        file_path = download_era5_daily(current_date)
        if file_path is None:
            print("  ✗ Download failed, skipping")
            failed += 1
            current_date += timedelta(days=1)
            continue
        
        # Process and archive
        if process_and_archive(file_path):
            print("  ✓ Successfully processed and archived")
            successful += 1
        else:
            print("  ✗ Processing failed")
            failed += 1
        
        current_date += timedelta(days=1)
    
    print(f"\nCompleted: {successful} successful, {failed} failed")


def example_5_custom_processing_workflow():
    """Implement custom processing workflow."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Custom processing workflow")
    print("="*70)
    
    from processing import process_daily_data, archive_file
    
    date = datetime(2024, 12, 1)
    date_str = date.strftime("%Y%m%d")
    
    # Simulate having a downloaded file
    from config import DATA_DIR
    test_file = DATA_DIR / f"era5_{ERA5_CONFIG['variable']}_{date_str}.nc"
    
    if test_file.exists():
        print(f"\nProcessing {test_file.name}...")
        
        # Your custom processing
        processed_file = process_daily_data(test_file)
        
        if processed_file:
            print(f"✓ Processed to: {processed_file}")
            
            # Archive
            archived_file = archive_file(processed_file)
            if archived_file:
                print(f"✓ Archived to: {archived_file}")
        else:
            print("✗ Processing failed")
    else:
        print(f"\nTest file not found: {test_file}")
        print("Run Example 1 first to create test data")


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("ERA5 PIPELINE - PROGRAMMATIC USAGE EXAMPLES")
    print("="*70)
    
    try:
        # Uncomment examples to run:
        
        # example_1_download_single_date()
        # example_2_download_with_custom_settings()
        # example_3_find_missing_files()
        # example_4_process_date_range()
        # example_5_custom_processing_workflow()
        
        print("\n" + "="*70)
        print("NOTE: Examples are commented out to prevent unwanted downloads.")
        print("Uncomment specific examples in main() to run them.")
        print("="*70)
        
        print("\nAvailable examples:")
        print("  1. Download single date")
        print("  2. Download with custom settings")
        print("  3. Find oldest missing file")
        print("  4. Process date range")
        print("  5. Custom processing workflow")
        
        print("\nUsage:")
        print("  python examples.py")
        print("\nOr uncomment examples in main() to run specific ones.")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
