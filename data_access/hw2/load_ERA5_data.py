### IMPORT MODULES
import ERA5_control_flow as cf


### PARAMETER TO CHANGE ###

VARIABLE = ["specific_humidity"]                        # change variable here
TIME = ["00:00", "06:00", "12:00","18:00"]              # download 6-hourly data
PRESSURE_LEVEL = ["300", "500", "800", "900", "975"]    # change pressure levels here

start = "2024-12-01"
end = "2024-12-05"

DATASET = "reanalysis-era5-pressure-levels"


cf.retrieve_and_process(DATASET, start, end, VARIABLE, TIME, PRESSURE_LEVEL)
