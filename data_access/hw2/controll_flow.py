import cdsapi
from datetime import datetime, timedelta
import healpy as hp

c = cdsapi.Client()




def retrieve_data(dataset, request, filename):
    
    client = cdsapi.Client()

    client.retrieve(dataset, request).download(filename)

def process_data(dataset, start, end, variable,time, pressure_level, data_format="netcdf", download_format = "unarchived" ):
    START_DATE = datetime.strptime(start, "%Y-%m-%d")
    END_DATE   = datetime.strptime(end, "%Y-%m-%d")

    current = START_DATE
    while current <= END_DATE:
        print(current)
        
        ### FILL REQUEST DICTIONARY

        REQUEST = {
                "product_type": ["reanalysis"],
                "variable": variable,
                "date": current.strftime("%Y-%m-%d"),
                "time": time,
                "pressure_level": pressure_level,
                "data_format": data_format,
                "download_format": download_format
            }

        FILENAME = "era5_specific_humidity_" + current.strftime("%Y-%m-%d") + "_6h_pl_new.nc"

        retrieve_data(dataset, REQUEST, FILENAME)

        current += timedelta(days=1)    