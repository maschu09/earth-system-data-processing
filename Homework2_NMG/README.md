\# Earth System Data Processing



Collection of notebooks and information on various aspects of Earth system data processing.



This repository contains material that has been provided for and developed during the lecture on

\*Earth System Data Processing\* at the University of Cologne in the winter semester 2025/26. The lecture

covered topics such as finding and accessing data from modern web services, coordinate systems,

remapping and interpolation, common file formats, types of Earth system data, numerical model grids,

metadata standards, FAIR data.



The course uses an inverse classroom concept, where the actual lectures are recorded, while students

discuss the lecture content and work on practical examples during the course hours. The material

in this repository forms the basis for the practical exercises. Students will also be assigned

coding tasks as homework and the best results have been included here to establish a collection of useful routines

for other students and scientists who wish to learn the basics of Earth system data processing.



\*Note:\* Due to the background of the lecturer, the focus of this material is on atmospheric data.

Nevertheless, many concepts and routines can also be applied to other Earth system data. Feel free to contribute

material for other data types if you find this repository useful.



\*Author:\* Martin Schultz, Jülich Supercomputing Centre, Forschungszentrum Jülich \& Department of Computer Science and Math, University of Cologne

October 2025





\## Homework 2: Automated ERA5 Processing Chain

\*\*Author: Nagibe Maroun González\*\*

\*\*Course: Earth System Data Processing WiSE 25/26\*\*







\### Overview

The second homework consists of a processing chain that downloads, process and stores data form the ERA5 dataset. The DailyRoutineERA5.py uses mock testing strategy to see if the workflow is successful.



This repository implements a robust, automated processing chain designed to download atmospheric data from the ERA5 dataset, perform spatial regridding, and archive the results in a Zarr format. The system is built to handle daily batches with a "catch-up" logic that automatically detects and processes missing days.



\### Files

'Homework\_2\_NagibeMG.ipynb': The main control notebook and visualization interface.

'RealDailyRoutineERA5.py': Contains the core logic for downloading, regridding, and saving.

'era5\_humidity.zarr': The output data store with the processed grids.

'DailyRoutineERA5.py': Contains the mock functions.





\### Dataset

ERA5-Land is a reanalysis dataset providing a consistent view of the evolution of land variables over several decades at an enhanced resolution compared to ERA5. ERA5-Land has been produced by replaying the land component of the ECMWF ERA5 climate reanalysis. Reanalysis combines model data with observations from across the world into a globally complete and consistent dataset using the laws of physics. Reanalysis produces data that goes several decades back in time, providing an accurate description of the climate of the past.

The chosen variable is relative humidity. However, the variable can be modified by the user (as well as other settings).



\### Implementation Details



1\. Control Flow:

The workflow is managed by a control function that scans a user-defined date range. Before processing a day, the script checks for a marker file. If the marker is missing, it triggers the pipeline: Download → Regrid → Store. This ensures that if the process is interrupted it will resume exactly where it left off.

2\. Dataset \& Variable Selection: The routine is fully flexible in terms of the data parameters. All user settings (dates, variables, levels, and hours) are passed as arguments from the notebook.

3\. Spatial Regridding: The processing chain converts the raw ERA5 Latitude-Longitude grid into a HEALPix (Hierarchical Equal Area isoLatitude Pixelization) grid (remapped to NSIDE 8 and NSIDE 16) using linear interpolation.

4\. Storage Strategy: Data is archived in a Zarr store using a group-based hierarchy and chunked by the time dimension (1 day per chunk) to optimize for time-series analysis.

5\. Visualization: It loads two arbitrary time samples and displays them. To ensure scientific comparability, all plots use a fixed color scale (0% to 100% Relative Humidity) and consistent colormaps (blue scale).







\### Challenges

Main issue is the unavailability of HEALPix for Windows, which is the OS that I use. Had to use a virtual machine and do all the configurations needed to run the program. This detour was very time consuming.

Current python version was not compatible with some libraries (dask), so had to create new environment with older py version to be able to run it. This issue was detected with the help of AI.



\### References

Copernicus Climate Change Service (C3S)(2019): ERA5-Land hourly data from 1950 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.e2161bac



