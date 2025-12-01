README – IMERG Global Precipitation (May 2024)

Homework 1 — IMERG Global Precipitation (May 2024)
Name: Mohammed Fawaz Nawaz
Email: mnawaz@smail.uni-koeln.de
Matriculation number: 7431597
Course: Earth System Data Processing 1 (ESDP1), WS 2025/26
Dataset: NASA GPM IMERG Half-Hourly (GPM_3IMERGHH.07)
Time Period: 1–3 May 2024
Notebook: load_imerg_mnawaz_may2024.ipynb

1. Introduction:

This README documents the process of identifying, accessing, and downloading the NASA IMERG Half-Hourly precipitation dataset for Homework 1. IMERG (Integrated Multi-satellitE Retrievals for GPM):

- provides global precipitation estimates

- has a 30-minute temporal resolution

- has a ~0.1° spatial resolution

- is produced by the Global Precipitation Measurement (GPM) mission

For this assignment:

- I used the period May 1–3, 2024

- Implemented a date loop over multiple days

- Performed date arithmetic (conversion to Day-of-Year)

- Accessed NASA GES DISC data via authenticated HTTP requests

2. Dataset Description:

Provider: NASA GES DISC
Product: IMERG Half-Hourly (3IMERGHH)
Version: V07B
Format: HDF5 (.HDF5)

Dataset characteristics:

- Temporal resolution: 30 minutes

- Spatial resolution: ~0.1°

- Coverage: Global

- Data volume: 48 files per day (~5–10 MB each)

Key IMERG variables

- precipitationCal – Gauge-calibrated precipitation rate

- precipitationUncal – Uncalibrated satellite-based estimate

- RandomError – Quantified uncertainty field

Official dataset page

🔗 https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary

3. Data Portal Evaluation & File Structure

To access IMERG, I explored the NASA GES DISC portal and documented the file organization.

Directory structure
/GPM_L3/GPM_3IMERGHH.07/YYYY/DOY/


YYYY = Year

DOY = Day of Year (e.g., 122 = 1 May 2024)

Example filename
3B-HHR.MS.MRG.3IMERG.20240501-S000000-E002959.0000.V07B.HDF5

Meaning of components

20240501 – Acquisition date

S000000 – Start time (00:00 UTC)

E002959 – End time (00:29 UTC)

V07B – Product version

The portal provides clean documentation, but downloading requires authenticated access.

4. Data Access Method (Authentication Required)

NASA IMERG data cannot be downloaded anonymously.

Requirements

- NASA Earthdata Login account

- Approval for: NASA GESDISC DATA ARCHIVE

- Programmatic access token (EDL Application Token)

Authentication methods tested
Method	Result
Username + Password	❌ 401 Unauthorized
.netrc machine credentials	❌ Failed
Cookies / redirect session	❌ Failed
Token-based Bearer Auth	✅ Successful
Final working solution

Generated an Application Token via Earthdata Profile

Used:

Authorization: Bearer <token>


in all HTTP requests through a requests.Session() object.

This method successfully authenticated and allowed file downloads.

5. Download Procedure Implemented

The notebook performs the following steps:

- Define date range: 2024-05-01 to 2024-05-03

- Convert dates to DOY

- Construct IMERG URLs (using YYYY + DOY)

- Apply token authentication via header

- Download one IMERG Half-Hourly file per day

- Save output to: imerg_data/

Example console output
Processing 2024-05-01
Downloaded successfully!
Processing 2024-05-02
Downloaded successfully!
Processing 2024-05-03
Downloaded successfully!


Files appear in the destination folder with expected sizes.

6. Problems Encountered & Solutions
✔ Authentication failures (main issue)

Issues observed:

- 401 errors despite correct credentials

- Portal login worked, but programmatic login did not

- .netrc, session cookies, and BasicAuth all failed

- DAAC approval alone was insufficient

Final solution:

- Use a NASA EDL Application Token

- Pass it as a Bearer token in request headers

- Directory + timestamp formatting

- IMERG uses DOY directories → required accurate conversion

- Filenames are long and require correct zero-padded timestamps

- Once solved, downloads worked reliably

- After applying token auth + correct paths, all files downloaded without error.

7. Scalability and Future Improvements

- If extending to longer periods (weeks–months):

Performance improvements

- Parallel/multiprocess downloading

- Retry logic for connection drops

- Buffered streaming for large files

Usability improvements

- Configurable date ranges

- Environment variable storage for tokens

- Logging instead of print() messages

S- torage considerations

- 48 files/day → ~0.5 GB per month

- Long-term archives can reach several GB

8. References

NASA GES DISC IMERG Dataset
https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary

IMERG Algorithm Documentation
https://gpm.nasa.gov/resources/documents/imerg-atbd

Earthdata Login
https://urs.earthdata.nasa.gov/