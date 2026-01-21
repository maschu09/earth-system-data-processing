# Explanation of the Code & Developement

When developing the download routine specified in the task description, I started by creating the basic functions for the logic of an expandable workflow. I will briefly explain these, referring to code cells 5 to 11. 

- daterange(start, end): The first function has the task of finding all data in a time series, specified by a start and end date, and storing it in an object of the Datetime module. 
- is_day_processed(day): This returns a Boolean value indicating whether a day has been processed. This information is based on whether a folder exists for the date in question.
- mock_process_day(day, fail_probability=0.2): As the name suggests, this function simulates the processing of data. A folder is created for the data to be processed, and a flagged .txt file is written to it. Additionally, a simulated failure is included, with a default probability of 20%.
- find_oldest_missing_day(start. end): If the entire time series is to be processed rather than just one day, this function uses the is_day_processed() function to search through all the dates to be processed and find the first one that has not yet been processed. It then returns this date as a datetime object. 
- find_oldest_processed_day(processed_dir, date_format): Here, the system searches for the oldest processed date. This function is used in the workflow when an entire time series is to be processed up to an end date, but no start date is provided by the user. To achieve this, the names of folders containing processed dates are read out and compared in chronological order.
- check_dates(start_date, end_date, target_date=None): A simple check to see whether the dates entered by the user make sense for an entire time series. Throws an error if the start date is after the end date. 
The target date is not checked here, as it is ultimately irrelevant to the logic of the workflow whether it falls within an additionally specified date range.
- run_daily_workflow(start_date=None, end_date=None, target_date=None): The actual control flow forms the core of the code. This brings together the individual parts explained above, and is expanded throughout the programme to include additional functionalities according to the task specification. 

The CDSAPI is used to download real data from the ERA5 database. You should already be familiar with both the database and the API from the lecture, so they will not be explained further here. To keep the download routine as flexible as possible, I have decided to use a configuration dictionary called 'ERA5_CONFIG'. Here, the query to the database could be adapted and modified. I also opted for the netCDF format because I feel more familiar with it. 
Ultimately, the query is outsourced to the 'download_era5_humidity(day)' function, which is only called in the workflow rather than for mock processing.

The sub-task of interpolating the data was where we first encountered real difficulties in development, which proved to be a significant challenge. As the Healpy module is no longer available for Windows, I chose to use the Hpgeom module instead. Although its scope is smaller, it is sufficient for the task at hand. 
The rather long runtime of around 20 minutes per date, and the two resolutions, made testing the interpolation function difficult. 
As with the ERA5 data download above, the 'interpolate_to_healpix(day, nside_list=[8, 16])' function is only called in the existing workflow once a date has been downloaded. This ensures that each date is fully interpolated before the next date is downloaded.

Initially, when choosing a suitable chunking strategy, I assumed that one time step would equal one chunk. However, I later decided to define a whole day, consisting of four time steps, as one chunk. This is because the smallest unit that we want to use most frequently for the given assignment is actually an entire day.
I also experienced significant difficulties when implementing this. Some modules do not appear to be compatible with each other without generating errors in all versions. You will find a note on the solution later in the manual.

For the graphical representation of the (processed) data, a 2x3 structure was chosen. Three plots are shown per line. From left to right, these represent the unprocessed original ERA5 data, the regridded NSIDE 8 resolution data and the regridded NSIDE 16 resolution data. Each row refers to a different point in time on the same day. This makes it very easy to compare the results and see the effect of the various operations on the data.  
As with downloading the ERA5 data, there is a dictionary for adjusting the configuration, and therefore the displayed data.

# Data Access

All data is downloaded from the ERA5 database via the CDS API. This requires a registered CDS user account, which can be set up at https://cds.climate.copernicus.eu/. Once a user has been created, the API must be configured locally. To do this, create a file named '.cdsapirc' in the folder 'C:\Users\YOUR_USER'. You can easily copy the contents of the file from your user profile under 'Your profile' > 'API key'. 
To send requests to the CDSAPI from Jupyter Notebook, you must first install and import the cdsapi module. You will find a corresponding check under the heading 'Check necessary modules' in the code that will install the module if it is missing.

# Manual

This Jupyter Notebook is a flexible download routine workflow for daily ERA5 humidity data. Besides the management of the download it also provides interpolation of the data and data storage in a Zarr file with chunking. 
It is intended that the function 'run_daily_complete_workflow()' be used, which combines all of the previously mentioned features except for the plotting. However, the individual components, as specified in the individual points of the assignment, can also be tested and checked separately from each other. 
Please use the following functions for this purpose:
 
- 'run_daily_workflow(start_date, end_date, target_date)' runs a mock processing to test the core control workflow that would handle daily data
- 'run_daily_era5_workflow(start_date, end_date, target_date)' extends the mock processing with a download of humidity data from ERA5 via CDSAPI
- 'run_daily_era5_interpolation_workflow(start_date, end_date, target_date, nside_list)' implements data interpolation with resolution nside = 8 and nside = 16
- 'run_daily_era5_interpolation_workflow_zarr(start_date, end_date, target_date, nside_list)' extends the workflow with appropriate chunking and storage of the interpolated data in Zarr format
- 'plot_data' loads two arbitrary points in time and plots the original and regridded data

As mentioned before, the function 'run_daily_complete_workflow()' is the final conclusion of the notebook that implements all single sub-functionalities besides the plotting of the data. In order to execute it, all other cells must first be executed in the order of the notebook. 
Note that the second cell block, labelled 'Check necessary modules', verifies that all the required modules, excluding the standard ones, are installed. This includes hpgeom, for example, which is required for interpolation calculations. If not, they are installed using the pip package installer. This may require the kernel to be restarted. If errors occur with one of the newly installed modules, it is advisable to restart the kernel. 
Furthermore, I recommend the following environment and checking the versions of the following modules if an unexpected error occurs.

- Python 3.11.5
- Zarr 2.8.1 
- Xarray 2023.6.0
- numcodecs=0.11.0
- typing_extensions 4.15.0
- xxhash-3.6.0

To modify the ERA5 download dynamically, e.g. to select a different variable or different pressure levels, adjust those in the configuration dictionary 'ERA5_CONFIG'. As stated in the code's inline comments, remember that dates must be passed as a 'date(yyyy, mm, dd)' object.

# Reflection on Code Improvements & Scalability

Overall, I am much happier with the code from the second submission than with the first. In my opinion, the code is much better structured and clearer this time around. Nevertheless, I think there is room for improvement. This applies in particular to scalability in relation to the runtime of the entire routine. The routine with interpolation takes a good 20 minutes per day for both resolutions. I imagine there must be a more efficient way to implement this.  
In addition, the code could be made more straightforward in some places. As it has grown steadily from one subtask to the next, some things could certainly be smoothed out afterwards. A concrete example of this is the fact that directories are still created centrally and statically. A dynamic solution would be much more convenient.
