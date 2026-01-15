import sys
import os
from datetime import datetime, timedelta

 
StartDate = datetime(2024, 12, 1)
EndDate = datetime(2024, 12, 5)
StoreZARR = "era5_humidity.zarr"

# mock routines

def check_if_processed(date):
    """
    Checks if a specific date already exists in our Zarr storage.
    """
    # this one is for mock file 
    return os.path.exists(f"mock_storage_{date.strftime('%Y%m%d')}.txt")

def daily_data_routine(date):
    """
    Processing chain: Download -> Regrid -> Save
    """
    print(f"\nStarting pipeline for: {date.strftime('%Y-%m-%d')}")
    
    # Mock Download
    if date.day == 2: # simulate a failure on Dec 2nd for testing
        print(f"Download failed for {date.strftime('%Y-%m-%d')}")
        return False
    
    print(f"Downloaded Humidity data.") 
    print(f"Regridding to HEALPix (NSIDE 8 and 16).") 
    print(f"Appending to Zarr store: {StoreZARR}") 
    
    # Dummy file to mark this day as done
    with open(f"mock_storage_{date.strftime('%Y%m%d')}.txt", "w") as f:
        f.write("done")
    return True

# control flow

def run_control_flow(date_arg=None):
    #date was provided
    if date_arg:
        desired_date = datetime.strptime(date_arg, "%Y-%m-%d")
        daily_data_routine(desired_date)
        return

    # no arguments - look for oldest missing file 
    print(f"Scanning for missing data between {StartDate.date()} and {EndDate.date()}...")
    
    current_date = StartDate
    while current_date <= EndDate:
        if not check_if_processed(current_date):
            success = daily_data_routine(current_date)
            # Handle successful and unsuccessful downloads 
            if not success:
                print("Stopping --> Routine failed.")
                break 
        else:
            print(f"{current_date.date()} exists --> Skipping.")
        
        current_date += timedelta(days=1)
