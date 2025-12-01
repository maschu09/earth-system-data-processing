**Author:** Johanna Kasischke
# LAB BOOK for homework 1
**Course:** ESDP
**Due Date:** 04.12.2025

## Homework assignment 1: Overview
The objective for this homework is to write a python code for downloading large volumes of data from environmental data servers. In more detail, the task requires to develop a storage concept and strategy for managing the downloads, including keeping track of which files have been transferred, as well as identifying those that failed. 

## Selection of data server
The chosen variable for this exercise is the sea surface temperature (SST), which has a critical impact on hurricane development. Since the earth is warming, the average sea surface temperature also rises, which may lead to more or heavier development of hurricanes. The focus area is the atlantic. Different servers were reviewed to find those that provided the necessary data. After comparing several options, NOAA CLASS satellite data was selected. The final dataset used comes from the NESDIS satellite programme, which provides historical SST data. 

### Initial attempt: NOAA CLASS GOES SST data
The intended datasat to use for this exercise was the Coastal Geostationary SST products from NOAA GOES and Japanese MTSAT-1R satellites (https://www.class.noaa.gov/saa/products/search?sub_id=0&datatype_family=GOESSST&submit.x=19&submit.y=4). The advantage of this dataset was the high temporal resolution. The focus time period should have been the recent hurricane Melissa in the carribean. Since the extraction of the received data didn't work out, a different dataset from the NOAA CLASS website was used. Besides, the download process for the GOES data will be shortly explained for other user to try their best in extracting the data.
It is first necessary to specify a time period. The advanced search function is not useful, because whenever the user chooses one of the "Datatype" or "Region" options, no data is found. This is suboptimal, because data must be downloaded, which may not be necessary. After defining a time period, the search button can be selected. A new window will then appear in which the datasets that are relevant to the user can be selected. In order to download these datasets, it is first necessary to register and then log in to one's account. Subsequently, the data can be requested for download. Upon completion of the process, the user is sent an e-mail a few hours later, in which it is stated that the data can be downloaded via FTP or via a link. After downloading the recipient will receive an ".gz" file, which requires decompression. It is unfortunate, but the file contained within the folder is not of a specific file format, and thus cannot be read by Linux programmes or Python scripts. Because of that the used dataset was changed for demonstrating purposes of this exercise.

### Final choice: NESDIS SST14NA dataset
Using this data, a closer look at how sea surface temperatures influence hurricane development in the Atlantic was taken. As the new data source only provided data up to 2016, the time period of interest was changed to the 2005 Atlantic Hurricane Season. This season lasted from 8 June 2005 to 6 January 2006. This season is historically significant (e.g. Hurricanes Katrina, Rita and Wilma).
A note on the website says that the product has been discontinued and that the alternative product is: Geo-Polar 5 km Global Night-time Only Blended SST. A big advantage of this dataset was, that the format netCDF was available and compatible with scientific python libraries (e.g. xarray). The used dataset can be also found in the folder for easy access. 

Please note: Adjusting the time period based on dataset availability is not ideal in real research. However, for this exercise, the workflow remains valid and transferable to other datasets.

## Download of the specific data
The NESDIS SST14NA dataset was accessed via: https://www.aev.class.noaa.gov/saa/products/welcome. The following steps need to be followed to download the data:
1. Navigate to the portal and select "Sea surface temperature (14 km North America)" either at the top search bar or on the right-hand side of the website.
2. Specify the temporal range (here: June 8 2005 till January 6 2006).
3. Choose output format (NetCDF preferred). Other options include ASCII, GIF, spreadsheet, tab-delimited or CSV.
4. Select the distributed variable (SST).
5. Initiate the search --> the server retrieves the specific data
6. The download starts by itself.

## Storage and management concept
To handle large datasets efficiently, the FAIR principles should be applied. Therefore it is necessary to design a useful directory hierarchy, in which raw and processed data are stored apart from each other. In a log-file changes to the data can be written down.
A metadata file should include all important information of the downloaded datafiles, such as download date, the status of the download, a source url and other necessary information. Additionally, an error handling strategy should be implemented. There should be a workflow about how to deal with failed downloads, corrupted files and duplicates.

## Evaluation of the respective data portal
Finding the appropiate dataset was uncomplicated, but the original data file caused technical difficulties. As a result, the dataset has to be switched, which is not ideal, because the new dataset provdies fewer data points and lacks the detail required for a real analysis. While general technical details about the dataset were easily available, obtaining more comprehensive or in-depth documentation was not straightforward. Another weakness of the dataset might be the discontinuation, especially, if one would want to use data which is younger than 2016. 

## Scientific context
Why does the sea surface temperature matters for hurricanes?
For a hurricane to develop, the SST needs to be greater than 26 °C according to Smith, R. K. and Montgomery, M. T. (2023). Because of the high temperatures in the carribean, tropical storms are very likely to develop there. An increase in SST would probably intensify the development of hurricanes in this region. The hurricane season of 2005 was exceptionally active, which makes it a strong case study.

There are some limitations of the SST14NA dataset. The regional coverage might exclude some parts of the atlantic, which might be necessary for a proper analysis. The resolution is only 14 km, so fine-scale ocean features might be missed. Because of the discontinued dataset, a comparison with more recent events is not possible.

# How to scale data access and make code more user-friendly
For this homework, only a limited dataset (one season) was downloaded. In real-world applications, researchers may need multi-year or global datasets, which introduces challenges:
1. Scalability:
    The python scripts (or any other programming language) must handle large volumes of data efficiently. Therefore, parallel downloads or an request prompt inside the python file could speed up the access. 
2. Storage:
    Large datasets require structured storage solutions such as large servers at the office or cloud storage.
   Access more data is with this dataset not a problem. With the GOES dataset, more datafiles would have been needed to download, which would have caused greater file sizes. If the file sizes would have been greater, there are several things to do to organize the data. This includes:
- group the data by year, month, day etc.
- group the data by region
- group the data by specific events inside the time period
4. user-friendly code:
    The provided scripts should incluede clear instructions in how to access the data and change the download volume. Therefore a good documentation is needed. The script itself should kept clear and simple.
5. Limits:
    There may be some limits to downloading the data from a source. This can be download quotas or server restrictions, network bandwidth or local storage capacity.

Applied to the used dataset, no information could be found in restrictions according to the maximum download quotas. 

# Literature
Smith, R. K. and Montgomery, M. T. (2023). Chapter 1 - observations of tropical cyclones. In Smith, R. K. and Montgomery, M. T., editors, Tropical Cyclones, volume 4 of Developments in Weather and Climate Science, pages 1–34. Elsevier.

