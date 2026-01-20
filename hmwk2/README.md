## Earth System Data Processing



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





##### Homework 2: Automated ERA5 Processing Chain

**Author: Nagibe Maroun González**



The second homework consists of a processing chain that downloads, process and stores data form the ERA5 dataset. The DailyRoutineERA5.py uses mock testing strategy to see if the workflow is successful.



##### Overview

This repository contains a processing chain for downloading ERA5 humidity data, regridding it to HEALPix, and saving it to a Zarr store. The workflow is designed to handle daily batches and recover from failures.



##### Files

* 'Homework\_2\_NagibeMG.ipynb': The main control notebook.
* 'RealDailyRoutineERA5.py': Contains the core logic for downloading, regridding, and saving.
* 'era5\_humidity.zarr': The output data store.
* 'DailyRoutineERA5.py': Contains the mock functions.



##### How to Run

Go to the jupyter notebook and run the cells in the order they are. 



##### Dataset

ERA5-Land is a reanalysis dataset providing a consistent view of the evolution of land variables over several decades at an enhanced resolution compared to ERA5. ERA5-Land has been produced by replaying the land component of the ECMWF ERA5 climate reanalysis. Reanalysis combines model data with observations from across the world into a globally complete and consistent dataset using the laws of physics. Reanalysis produces data that goes several decades back in time, providing an accurate description of the climate of the past.

The chosen variable is relative humidity. However, the variable can be modified by the user (as well as other settings).



##### Data processing 

The processing chain includes a spatial transformation step to convert the ERA5 data from its native format to a HEALPix (Hierarchical Equal Area isoLatitude Pixelization) grid. 

* Original Data Structure: The raw ERA5 data is retrieved on a regular Latitude-Longitude grid (Plate Carrée projection). In this format, the data is stored as a 2D matrix (latitude x longitude), where the physical area of each grid cell decreases significantly towards the poles due to meridian convergence.
* Target Grid: The data is interpolated onto a HEALPix grid with two distinct resolutions: NSIDE 8 (coarse) and NSIDE 16 (finer). Unlike the lat-lon grid, HEALPix divides the sphere into pixels of equal surface area, which is critical for unbiased global statistical analysis. The resulting data structure flattens the 2D spatial dimensions into a single 1D dimension (healpix\_pixel).
* Interpolation Method: The transformation is performed using linear interpolation. This method calculates the value for each HEALPix pixel center by taking the weighted average of the four nearest neighbors from the original ERA5 source grid, ensuring a smooth transition of values between the two coordinate systems.



##### Challenges

1. Main issue is the unavailability of HEALPix for Windows, which is the OS that I use. 



##### References

Copernicus Climate Change Service (C3S)(2019): ERA5-Land hourly data from 1950 to present. Copernicus Climate Change Service (C3S) Climate Data Store (CDS). DOI: 10.24381/cds.e2161bac

