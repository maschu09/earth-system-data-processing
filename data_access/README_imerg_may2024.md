# Homework 1 — IMERG Global Precipitation (May 2024)

**Name:** Mohammed Fawaz Nawaz
**Email:** [mnawaz@smail.uni-koeln.de](mailto:mnawaz@smail.uni-koeln.de)
**Matriculation number:** 7431597
**Course:** Earth System Data Processing 1 (ESDP1), WS 2025/26
**Dataset:** NASA GPM IMERG Half-Hourly (GPM_3IMERGHH.07)
**Time Period:** 1–3 May 2024
**Notebook:** load_imerg_mnawaz_may2024.ipynb

---

# 1. Introduction

This document describes the process of identifying, accessing, and downloading the NASA IMERG Half-Hourly precipitation dataset for Homework 1. IMERG (Integrated Multi-satellitE Retrievals for GPM) is a global precipitation product produced by the Global Precipitation Measurement (GPM) mission. It provides precipitation estimates every 30 minutes with a spatial resolution of approximately 0.1°.

For this assignment, I worked with the time period 1–3 May 2024. This range satisfies the requirement to implement a loop across multiple days and perform simple date arithmetic. The aim of the homework is to explore dataset structure, understand data access requirements, and document the entire workflow clearly.

---

# 2. Dataset Description

The IMERG dataset is distributed by NASA’s Goddard Earth Sciences Data and Information Services Center (GES DISC). It combines input from multiple microwave, radar, and infrared sensors to generate a global precipitation field.

Dataset characteristics:

* Temporal resolution: 30 minutes
* Spatial resolution: ~0.1°
* Spatial coverage: Global
* Data format: HDF5 (.HDF5)
* Product version: V07B

Important IMERG variables:

* precipitationCal – gauge-calibrated precipitation rate
* precipitationUncal – uncalibrated retrieval
* RandomError – uncertainty estimate

Official dataset documentation:
[https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary)

---

# 3. Data Portal Evaluation and File Structure

IMERG data is organized in a hierarchical directory system on NASA GES DISC. Files are stored by year and day-of-year (DOY).

Directory structure:
/GPM_L3/GPM_3IMERGHH.07/YYYY/DOY/

For example, 1 May 2024 corresponds to DOY 122.

Example IMERG file name:
3B-HHR.MS.MRG.3IMERG.20240501-S000000-E002959.0000.V07B.HDF5

Meaning of components:

* 20240501 → date
* S000000 → start time (00:00 UTC)
* E002959 → end time (00:29 UTC)
* V07B → product version

The metadata and structure were easy to understand, but downloading required authentication.

---

# 4. Data Access Method and Authentication

IMERG Half-Hourly data requires NASA Earthdata Login authentication. Anonymous access is not allowed.

Requirements:

* NASA Earthdata Login account
* Approval for “NASA GESDISC DATA ARCHIVE”
* EDL Application Token for programmatic downloads

Authentication methods tested:

* Username + password → failed (401)
* .netrc machine credentials → failed
* Cookie/session methods → failed
* BasicAuth → failed
* EDL Application Token → successful

Final working method uses:
Authorization: Bearer <token>

The token is generated in Earthdata Login under “Applications”.

---

# 5. Download Implementation

The notebook automates downloading one IMERG Half-Hourly file for each day in the range 1–3 May 2024.

Steps in the script:

* Define start and end dates
* Convert dates to day-of-year (DOY)
* Construct IMERG file names
* Build download URLs
* Create authenticated session with token
* Save files into the folder “imerg_data/”

The script output confirmed all files downloaded successfully.

---

# 6. Challenges and Solutions

Authentication issues:

* Most login methods returned 401 errors
* The final solution was using the NASA EDL Application Token

Directory structure and naming:

* IMERG uses DOY indexing, requiring conversion
* File names are long and require precise formatting

Access permissions:

* DAAC approval was required
* Token-based authentication was essential

Once the correct authentication workflow was in place, downloading was straightforward.

---

# 7. Scalability and Future Improvements

For larger downloads such as full months or years, several improvements can be implemented:

* Parallel or asynchronous downloads
* Retry logic for network failures
* Logging instead of print statements
* Environment variables for storing sensitive tokens
* Automatic creation of structured subfolders
* Flexible user-defined date ranges

Given that IMERG produces 48 files per day, performance and storage planning are important.

---

# 8. References

* NASA GES DISC IMERG Dataset:
  [https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary](https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary)

* IMERG Algorithm Documentation (ATBD):
  [https://gpm.nasa.gov/resources/documents/imerg-atbd](https://gpm.nasa.gov/resources/documents/imerg-atbd)

* NASA Earthdata Login:
  [https://urs.earthdata.nasa.gov/](https://urs.earthdata.nasa.gov/)

# 9. Reflections and Learning Experience

Working with the IMERG dataset provided valuable hands-on experience in accessing real-world satellite precipitation products. Beyond the technical steps, this homework helped me understand several important aspects of Earth system data processing:

I learned how global precipitation data is structured, stored, and distributed at NASA GES DISC.

I gained practical experience with authentication workflows, including understanding why certain datasets require login even when advertised as “open”.

I became more comfortable working with Day-of-Year indexing, long filenames, and programmatic URL construction.

Dealing with repeated 401 errors helped me understand the importance of persistence and debugging when working with scientific data portals.

Successfully downloading the IMERG dataset after solving authentication issues felt rewarding and helped build confidence in handling remote-sensing datasets.

I now appreciate how even a “simple” task like downloading a few days of data involves understanding APIs, tokens, file structures, and metadata.

Overall, this homework was not only about accessing precipitation data but also about learning how to interact with real Earth science data systems that researchers around the world use every day.