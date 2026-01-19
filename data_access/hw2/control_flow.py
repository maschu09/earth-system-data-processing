import argparse
import random
from datetime import datetime, timedelta, date

# Define start and end date for download routine
START_DATE = date(2026, 1, 1)       # Begin of project
ARCHIVE = set()                     # mocks a folder of finished days

def download_data(day):
    """
    This function "downloads" data and fails randomly. 
    """
    if random.random() < 0.3:  # 30% failure rate
        raise ConnectionError(f"Download failed for {day}")
    print(f"  [1/3] Downloaded data for {day}")

def process_data(day):
    """
    Process test data.
    """
    print(f"  [2/3] Processed data for {day}")

def archive_data(day):
    """
    Add downloaded data to archive.
    """
    ARCHIVE.add(day)
    print(f"  [3/3] Archived {day}")

def run_pipeline(day):
    """
    This function contains the whole control flow for downloading data. 
    In this case nothing is really downloaded.
    """
    print(f"\n--- Starting Pipeline for {day} ---")
    try:
        if day in ARCHIVE:
            print(f"  Skipping {day}: Already archived.")
            return True
        
        download_data(day)
        process_data(day)
        archive_data(day)
        return True
    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    
# need to call pipeline function
def main():
    parser = argparse.ArgumentParser(description="Daily Data Manager")
    parser.add_argument("--date", type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(), 
                        help="Process a specific date (YYYY-MM-DD)")
    args = parser.parse_args()

    if args.date:
        # Scenario 1: Specific date requested
        run_pipeline(args.date)
    else:
        # Scenario 2: Find gaps and process until today
        today = date.today()
        current = START_DATE
        print(f"Auto-syncing from {START_DATE} to {today}...")

        while current <= today:
            if current not in ARCHIVE:
                success = run_pipeline(current)
                if not success:
                    print(f"Stopping at {current} due to failure.")
                    break
            current += timedelta(days=1)

if __name__ == "__main__":
    # Pre-filling archive with some "finished" dates to test gap detection
    ARCHIVE.add(date(2026, 1, 1))
    ARCHIVE.add(date(2026, 1, 2))
    
    main()