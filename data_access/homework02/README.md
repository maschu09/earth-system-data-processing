# Manual

This Jupyter Notebook is a flexible download routine workflow for daily ERA5 humidity data. Besides the management of the download it also provides interpolation of the data and data storage in a Zarr file with chunking. 
It is intended that the function run_daily_complete_workflow() be used, which combines all of the previously mentioned features except for the plotting. However, the individual components, as specified in the individual points of the assignment, can also be tested and checked separately from each other. 
Please use the following functions for this purpose:
 
‘run_daily_workflow(start_date, end_date, target_date)’ runs a mock processing to test the core control workflow that would handle daily data
‘run_daily_era5_workflow(start_date, end_date, target_date)’ extends the mock processing with a download of humidity data from ERA5 via CDSAPI
‘run_daily_era5_interpolation_workflow(start_date, end_date, target_date, nside_list)’ implements data interpolation with resolution nside = 8 and nside = 16
‘run_daily_era5_interpolation_workflow_zarr(start_date, end_date, target_date, nside_list)’ extends the workflow with appropriate chunking and storage of the interpolated data in Zarr format
‘plot_data’ loads two arbitrary points in time and plots the original and regridded data

As mentioned before, the function run_daily_complete_workflow() is the final conclusion of the notebook that implements all single sub-functionalities besides the plotting of the data. In order to execute it, all other cells must first be executed in the order of the notebook. 
Note that the second cell block, labelled 'Check necessary modules', verifies that all the required modules, excluding the standard ones, are installed. This includes hpgeom, for example, which is required for interpolation calculations. If not, they are installed using the pip package installer. This may require the kernel to be restarted. If errors occur with one of the newly installed modules, it is advisable to restart the kernel. 
Furthermore, I recommend the following environment and checking the versions of the following modules if an unexpected error occurs.

Python 3.11.5
Zarr 2.8.1 
Xarray 2023.6.0
numcodecs=0.11.0
typing_extensions 4.15.0
xxhash-3.6.0

To modify the ERA5 download dynamically, e.g. to select a different variable or different pressure levels, adjust those in the configuration dictionary ‘ERA5_CONFIG’. As stated in the code's inline comments, remember that dates must be passed as a 'date(yyyy, mm, dd)' object.

# Code improvements and scalability

Overall, I am much happier with the code from the second submission than with the first. In my opinion, the code is much better structured and clearer this time around. Nevertheless, I think there is room for improvement. This applies in particular to scalability in relation to the runtime of the entire routine. The routine with interpolation takes a good 20 minutes per day for both resolutions. I imagine there must be a more efficient way to implement this.  
