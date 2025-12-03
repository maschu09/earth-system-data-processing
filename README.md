# Homework 1
Student: Florian Bremm <br>
MatNr.: 7440728

## General Information

The contribution of this fork is the `load_sentinel1.ipynb`. This notebook can be used to download Radar Data of the Sentinel 1 Mission. This Data has various applications in different fields, mainly Climatology, Environment, Transport, Economy, Security. In its current form the notebook downloads the vv and vh bands as well as their median (vv&vh). All Bands are averaged over the timespan of one month, thereby making sure every place in the area of interest is covered and there are no blank spots. Additionally, it reduces the time needed to complete the download, due to the main bottleneck being the data providing for download on the server, not the download itself.

## Data Access
To access the data, authentication is required. However, access is granted to every person and registration requires less than 5 Minutes. Visit https://dataspace.copernicus.eu/ for registration. After registration is completed online, this client must be registered interactively during notebook execution. This process provides minimal friction, compared to a system with a token that must be manually created and provided to the client. See `load_sentinel1.ipynb` for details.

## Data Format
I have decided to store the data in GeoTiff format, as it has built in localisation is more memory efficient than ASCII based formats like csv or json. Additionally, there are tools to instantly view GeoTiff (one such tool is available at https://www.pozyx.io/free-tools/online-geotiff-viewer).

## Area of Interest
I chose a range from Zeeland in the Netherlands to Esbjerk in Denmark, as this area contains a variety of different landmarks that highlight the capabilities of Sentinel 1. The stride of 1 deg was chosen because the openeo api specifications state, that their api wasdesigned to handle up to 100x100km at a resolution of 10x10m per pixel. 1deg x 1deg roughly matches that. As agreed on in class I chose May 2024 as month.

## Scalability
At the moment, this notebook isn't very scalable. As mentioned the bottleneck appears to be the data-retrival on the server, as there is no notable spike in network activity and the created files are magnitudes smaller than the maximum bandwidth volume for the downloading time. However, I noted that downloading a single day of a 1deg x 1deg plain takes eight minutes, while downloading the month mean for the same plain takes roughly double that time (the mean is created on server side). Therefore, it is apparently beneficial to the download time to download bigger chunks from server. This is however limited by the memory capacity of my local machine. This optimization could easily be harnessed with high performance compute or even higher end consumer electronics.

Because servers are usually set up to handle many incoming connections, parallelisation is another possible optimisation. The openEO Api and Client library even provide in-house capabilities for parallelisation. With this, the execution time for the download could be reduced significantly.

*Author:* Florian Bremm, Department of Computer Science and Math, University of Cologne December 2025