## Exploring NASA GPM IMERG Precipitation Data (Half-Hourly, V07 Final Run)

Author: Gaurav Somani

### 1. Dataset Identification

I started my search by browsing different Earth system datasets listed in the homework instructions. NASA **GPM IMERG precipitation dataset** immediately caught my interest, because I work with ground-based rain-rate measurements (e.g., Parsivel disdrometers). I wanted to understand how global precipitation products compare. IMERG will help me explore precipitation from a global, satellite-based perspective rather than point-wise ground sensors.

I selected **IMERG Half-Hourly Final Run (V07)** because:

- Global precipitation coverage  
- 0.1° × 0.1° spatial resolution  
- 30-minute temporal resolution  
- Freely available  
- Well documented  
- Perfect for data-access workflow evaluation  

---

## 2. Searching & Navigating Data Portals

NASA organizes satellite precipitation products into processing “levels”:

- **Level 1** – Instrument measurements that have been calibrated, geolocated, and converted into sensor units (e.g., brightness temperatures).  
- **Level 2** – Geophysical variables retrieved from Level 1 data at the same spatial/temporal resolution (e.g., rain rate from microwave retrievals).  
- **Level 3** – Spatially and/or temporally resampled datasets derived from Level 1/2. These are gridded, analysis-ready products.

IMERG **Level 3** merges observations from multiple microwave and infrared sensors and produces global precipitation fields on a uniform 0.1° × 0.1° grid.

For this homework, I focused on:

- **GPM_3IMERGHH.07** — Half-hourly, Version 07 (30 min)  
  https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary?keywords=%22IMERG%20final%22

Other IMERG Final Run products include:  
- **Daily**: https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGDF_07/summary?keywords=%22IMERG%20final%22  
- **Monthly**: https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGM_07/summary?keywords=%22IMERG%20final%22  

Within the half-hourly dataset, NASA provides three processing runs:  
- **Early (HHE)** – available quickly, lower-quality  
- **Late (HHL)** – improved latency and calibration  
- **Final (HHR)** – highest-quality, gauge-corrected product  

Since the Final Run (HHR) is the most accurate and intended for research, I selected it for this work.

Directory layout:
/YEAR/DAY-OF-YEAR (001–365)/
  ├── 48 × half-hourly HDF5 data files
  └── 48 × matching XML metadata files

Example directory I worked with:

https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHH.07/2025/121/


---


### 3. Dataset Documentation

NASA provides excellent documentation. The following URLs were essential:

####  IMERG Product Overview  
https://gpm.nasa.gov/data/imerg

#### FAQ for IMERG V07 Applications Users_202502.pdf 
https://gpm.nasa.gov/media/708

#### GES DISC IMERG Product Page  
https://disc.gsfc.nasa.gov/datasets/GPM_3IMERGHH_07/summary

Everything was well linked and beginner-friendly.

---

### 4. Authentication & Technical Workflow
Before downloading, I created an Earthdata Login account  
(https://urs.earthdata.nasa.gov/home).  
To enable programmatic access, I went to the **Applications** tab and approved the  
**NASA GESDISC DATA ARCHIVE** application. This authorization is required for accessing IMERG files via HTTPS.
Earthdata Login also provides access to many other NASA data archives.  
Users can approve additional applications in the same way, depending on which datasets they want to access. 

GES DISC uses standard Earthdata Login authentication; no additional API token is needed.



####  Creating `.netrc`

```bash
vi ~/.netrc
```
Contents:
```bash
machine urs.earthdata.nasa.gov
    login <my-email>
    password <my-password>
```
NASA requires strict permissions, so I set:
```bash
chmod 600 ~/.netrc
```

Python authenticated download:

```python
session = requests.Session()
session.trust_env = True
```
Working with HDF5
```python
import h5py

f = h5py.File("example.h5", "r")
list(f["Grid"].keys())
```

This gave access to:

- precipitation
- randomError
- probabilityLiquidPrecipitation
- precipitationQualityIndex
- lat, lon
- time, time_bnds
  
Opening HDF5 files with the h5py library was straightforward — I could inspect the dataset tree, shapes, metadata, and attributes easily.
The only limitation is that IMERG files must be downloaded entirely; variable-level subsetting isn’t supported.

---

### 5. Understanding the File Structure

The naming convention was intuitive after brief inspection:

Example:
```
3B-HHR.MS.MRG.3IMERG.20250502-S000000-E002959.0000.V07B.HDF5
```

Meaning:
- 20250502-Date
- S000000–E002959-00:00–00:29 UTC
- 48 such files per day
- V07B-Version
- HHR-Half-hourly Final Run ("HH"=Half-hourly, “R” = Final)
- Daily directory structure uses Day-of-Year (DOY), e.g.: 121=2 May 2025

Once I understood this, navigation was trivial.

---

### 6. Evaluation of the Data Portal (GES DISC)

Overall, the GES DISC portal was extremely smooth to use:

- Clean folder structure
- Clear documentation
- Simple Earthdata authentication
- No API complexities (just .netrc)
- Direct HTML directory listings
- Fast downloads
- Beginner friendly
- GUI and Python both supported

Only drawback:
You must download full HDF5 files rather than selecting individual variables.
Otherwise, it is an excellent, accessible, well-organized platform for scientific data.

---

### 7. AI Assistance Documentation

I used ChatGPT for the following verified queries:

- Setting up a `.netrc` file for NASA Earthdata authentication:
  - Helped me switch from `nano` (not installed) to `vi`
  - Helped ensure correct indentation and permissions

- Opening an HDF5 file with `h5py`:
  - I had never parsed HDF5 before
  - ChatGPT helped me explore the tree structure and attributes

- I also used AI assistance to extract precipitation values for Cologne and Kolkata, 
and to search the IMERG grid for locations with non-zero precipitation on May 1, 2025. 
