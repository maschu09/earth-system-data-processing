# LAB BOOK for homework 1
**Course:** ESDP
**Author:** Johanna Kasischke
**Due Date:** 04.12.2025

## Homework assignment 1: Overview
For this homework, we should create a script for downloading large amounts of data from a specific server. We should also develop a storage concept and a strategy for managing the downloads, including keeping track of which files have been transferred, as well as identifying those that failed.

## Select data server
For this exercise, I wanted to work with meteorological data, particularly the "sea surface temperature" variable. I therefore looked at different servers to find those that provided the necessary data. I therefore opted for NOAA CLASS satellite data. Initially, I intended to work with GOES satellite data, but extraction into a useful format was unsuccessful, I switched to historical data from the NESDIS programme. 

Using this data, I wanted to take a closer look at how sea surface temperatures influence hurricane development in the Atlantic. As the new data source
only provided data up to 2016, I changed the time period of interest to the 2005 Atlantic Hurricane Season. This season lasted from 8 June 2005 to 6 January 2006. A note on the website says that the product has been discontinued and that the alternative product is: Geo-Polar 5 km Global Night-time Only Blended SST. Please note that changing the time period or region of interest just depending on the availability of data is not the right way. I think, for this exercise it's fine, because the learnings can be applied on every other data server.

### Short notice and explanation on the GOES data
The primary objective was to utilise the Coastal Geostationary Sea Surface Temperature products from the NOAA GOES and Japanese MTSAT-1R satellites (https://www.class.noaa.gov/saa/products/search?sub_id=0&datatype_family=GOESSST&submit.x=19&submit.y=4). The process of downloading data from this website is a little bit different. In this instance, it is first necessary to specify a time period. The advanced search function is not useful, because whenever the user chooses one of the "Datatype" or "Region" options, no data is found. This is suboptimal, because data must be downloaded, which may not be necessary. After defining a time period, the search button can be selected. A new window will then appear in which the datasets that are relevant to the user can be selected. In order to download these datasets, it is first necessary to register and then log in to one's account. Subsequently, the data can be requested for download. Upon completion of the process, the user is sent an e-mail a few hours later, in which it is stated that the data can be downloaded via FTP or via a link. After downloading the recipient will receive an ".gz" file, which requires decompression. It is unfortunate, but the file contained within the folder is not of a specific file format, and thus cannot be read by Linux programmes or Python scripts. Because of that I changed the dataset.

## Download the specific data
The following website contains the data required for this study: https://www.aev.class.noaa.gov/saa/products/welcome. The data is available for download by searching for it on the right-hand side of the website. The chosen dataset was the "Sea Surface Temperature data (SST) (14 km North America) (SST14NA)". A new window appears and then the temporal range can be specified. Additionally the output file type (NetCDF file, plotted image GIF, generic ASCII file, spreadsheet, tab delimited file, comma delimited file) and the distributed variable can be chosen. The user can initiate a search by selecting the search button. The server is retrieving the specified data.

## Evaluation of the respective data portal
Finding the appropriate dataset was uncomplicated, but the original data file caused technical difficulties. As a result, I had to switch to a different dataset, which is not ideal because it provides fewer data points and lacks the detail required for my analysis. While general technical details about the dataset were easily available, obtaining more comprehensive or in-depth documentation was not straightforward.

## Please note
It should be noted that the quantity of data downloaded is minimal. It can be assumed that the preferred data set would have been more beneficial, with the inclusion of more detailed data.



