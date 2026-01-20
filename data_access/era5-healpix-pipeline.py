import os
from datetime import datetime, timedelta


class ERA5HealpixPipeline:
    def __init__(self, data_dir="/data/era5/healpix/"):
        self.data_dir = data_dir

    def process_and_archive_daily_data(
        self,
        end_date = None, 
        fixed_date = None,
        debug = False                       # if True, it will not download actual data
    ):
        assert not (end_date and fixed_date), "Provide either end_date or fixed_date, not both."

        start_date, end_date = self._get_start_and_end_dates(end_date, fixed_date)
        

    def _get_start_and_end_dates(self, end_date, fixed_date):
        # if no end_date is provided, use today's date
        if not end_date and not fixed_date:
            end_date = datetime.now(datetime.timezone.utc).date()

        if fixed_date:
            start_date = fixed_date
            end_date = fixed_date
        else:
            # find latest date in data directory
            latest_date = None
            for entry in os.listdir(self.data_dir):
                try:
                    date_string = entry.split('.')[0]
                    entry_date = datetime.strptime(date_string, "%Y-%m-%d").date()
                    if not latest_date or entry_date > latest_date:
                        latest_date = entry_date
                except ValueError:
                    continue

    def download_data_for_date(self, date):
        # Placeholder for actual download logic
        print(f"Downloading data for {date}...")

    def process_data_for_date(self, date):
        # Placeholder for actual processing logic
        print(f"Processing data for {date}...")

    def archive_data_for_date(self, date):
        # Placeholder for actual archiving logic
        print(f"Archiving data for {date}...")