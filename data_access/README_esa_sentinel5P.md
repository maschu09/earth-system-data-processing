# README — Sentinel-5P $NO_2$ Data Access (Author: Patrick Seidel)

This repository provides a documented and reproducible workflow to access, download, and preprocess **Sentinel-5P Level-2 $NO_2$ tropospheric column data** from the **Copernicus Data Space Ecosystem (CDSE)** using the **Sentinel Hub Process API**. The final output is a locally stored collection of daily GeoTIFFs and a combined NetCDF dataset for scientific reuse.

---

## 1. Dataset Discovery and Selection

### Objective  
I decided, that I wanted to download data about the reduced air pollution during the Covid-19 pandemic period. A quick google search showed me that the tropospheric $NO_2$ values are good measure for that, and that the Senintel-5P satellite carries an instrument to measure this.

### Identification Process  
I explored the Copernicus Data Space documentation and used the dataset overview pages:  
- Sentinel-5P mission description: https://dataspace.copernicus.eu/explore-data/data-collections/sentinel-data/sentinel-5p  
- Sentinel-5P $NO_2$ L2 product: https://sentinels.copernicus.eu/data-products/-/asset_publisher/fp37fc19FN8F/content/sentinel-5-precursor-level-2-nitrogen-dioxide  

### Short Dataset Description  
- **Sensor:** Sentinel-5P TROPOMI  
- **Variable:** Tropospheric $NO_2$ column density (mol/m²), Level-2  
- **Spatial resolution:** approx. 3.5 × 5.5 km since August 2019  
- **Temporal resolution:** one overpass per day at mid-latitudes  
- **Processing:** Geophysical retrieval operated by ESA; data distributed via CDSE  

---

## 2. Data Access and Interfaces

CDSE offers several access mechanisms:

**Catalog APIs:** -> STAC / OData / OpenSearch
- grant access to unprocessed L1 data
- each datasource (e.g. a satellite) is a "collection", each measurement variable (e.g. $NO_2$) is a "product"
- each collection and product are processed differently with extensive documentation

**Streamlined Access:**

1. **openEO**
  - connect to copernicus dataspace ecosystem (cdse)
  - choose collection, e.g. Sentinel 5P
  - run aggregation jobs in the cloud
  - download result as NetCDF
2. **Sentinel Hub**
  - search, process and download data and statistics from CDSE cloud
  - **catalog API** is to search for data, using STAC spec
  - **process API** is the most valuable tool to us
    - we provide JavaScript eval scripts that define input and output then send a request, which specifies the resolution, bbox, data collection and outputs geotiff data
  - **statistical API** to calculate statistics, like average $NO_2$ value over a month in the cloud, instead of downloading data and calculating locally

For this homework, the **Sentinel Hub Process API** is optimal:
- Supports **daily temporal slices**  
- Full control using **Python**  
- Allows downloading raw L2 pixels with custom resolution and bounding boxes  
- Requires only an evalscript and a REST request  

Relevant documentation:  
* https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/
* https://documentation.dataspace.copernicus.eu/notebook-samples/sentinelhub/air_pollution_statistics.html#analysing-spatial-distribution

I tried using openEO too (see [this commit](https://github.com/PaSeidel/earth-system-data-processing/commit/d68f6d92a6a9e45571e7924dc7ebfc1917791231)), but I kept running into errors of their backend, so I switched to Sentinel Hub.

---

## 3. Authentication and Setup

1. Create a CDSE account: https://documentation.dataspace.copernicus.eu/Registration.html  
2. Create OAuth client credentials  
3. Use the Python package `sentinelhub` to authenticate:

```python
from sentinelhub import SHConfig

config = SHConfig()
config.sh_client_id = "<client_id>"
config.sh_client_secret = "<client_secret>"
config.save()
```

---

## 4. Download Workflow (Notebook Summary)

The notebook `load-esa-sentinel5P.ipynb` performs:

### (a) Define Area of Interest
Example: Ruhrgebiet region.

```python
from sentinelhub import BBox, CRS
ruhrgebiet_coords_wgs84 = [6.380946, 51.315164, 7.93203, 51.738085]
aoi_bbox = BBox(bbox=ruhrgebiet_coords_wgs84, crs=CRS.WGS84).transform(CRS(3857))
```

I got the coordinates, using the [Sentinel Hub Request Builder](https://apps.sentinel-hub.com/requests-builder/).

### (b) Build Daily Time Intervals
```python
import pandas as pd

daily_intervals = [
    (
      day.strftime("%Y-%m-%dT00:00:00Z"),
      day.strftime("%Y-%m-%dT23:59:59Z")
    )
      for day in pd.date_range(start, end, freq=freq)
]
```

### (c) Evalscript for $NO_2$ + datamask
```javascript
//VERSION=3
function setup() {
   return {
    input: ["NO2", "dataMask"],
    output: 
      {
        id: "default",
        bands: 1,
        sampleType: "FLOAT32"
      },
    mosaicking: "SIMPLE"
  };
}
function evaluatePixel(sample) {
  if (sample.dataMask == 1)  {
    return [sample.NO2];
  } else {
    return [NaN];
  }
}
```
* specifies which band to use ($NO_2$)
* uses QA tool of TROPOMI to output NaN values if not data was recorded, e.g. because of overcast

### (d) Execute Daily Process API Requests
The notebook loops over all daily intervals, downloads a GeoTIFF per day, and writes them into a dated folder structure:

```
data/ruhrgebiet/YYYY-MM-DD/<request-id>/response.tiff
```

Each TIFF contains one daily overpass of $NO_2$ over the AOI.  
The code also records:
- request duration  
- success/failure  
- fraction of valid pixels  
- daily mean value  
A summary DataFrame is produced.

For the specified AOI (Ruhrgebiet, ca. 5057.45 $km^2$) and a time range of six years, the combined download time was around 50 min.

### (e) Convert Downloaded TIFFs into a Single NetCDF
All daily TIFF rasters are stacked into one 3-D array (`time × y × x`) and exported:

```python
import xarray as xr
ds = xr.Dataset(
    data_vars={
        "NO2": (("time", "y", "x"), data_stack)
    },
    coords={
        "time": dates,
        "y": lat,
        "x": lon,
    },
    attrs=attr_dict
)
ds.to_netcdf("no2_ruhrgebiet_daily.nc")
```

This NetCDF is ready for downstream scientific analysis.

---

## 5. Working Example Result

The notebook successfully downloads **6 years of daily $NO_2$ scenes for the Ruhrgebiet**, stores each TIFF, and aggregates them into a single NetCDF file. A simple time-series visualization (daily regional mean $NO_2$) demonstrates the ability to load and process the dataset.

---

## 6. Development Path (What Worked / What Changed)

- Started with dataset survey inside CDSE; identified Sentinel-5P $NO_2$ as the most relevant air-quality indicator for COVID-19 analysis.  
- Experimented with openEO, but Sentinel-5P backend limitations caused repeated failures.  
- Switched to Sentinel Hub’s Process API, which proved more stable and consistent.  
- Developed daily temporal slicing, fixed evalscript band mismatch, ensured proper CRS handling, and validated pixel availability with `dataMask`.  
- Implemented automated quality diagnostics and final NetCDF conversion.  
- Stored all steps in a reproducible Jupyter notebook.

---

## 7. Scalability Considerations

If users require data for **months to years**, changes are necessary:

### Technical Limits
- CDSE throttles request rates and processing units per user (30k request per month per user, currently one day is one request)
- Per-day Process API calls scale linearly with time span; hundreds of days become slow.

### How to Scale
- Batch requests via the Process API (weekly or monthly windows where appropriate)  
- Use the **Statistical API** for cloud-side temporal averaging (reduces data volume dramatically)  
- Parallelize daily requests with Python async/ThreadPool (respectful of rate limits)  
- Store results in chunked **NetCDF/Zarr** for scalable downstream analysis  
- Use coarser resolution or smaller AOIs for long time series

### Practical Upper Bound
Downloading the full global Sentinel-5P $NO_2$ archive is infeasible due to:
- cloud compute limits  
- quota on processing units  
- practical time to retrieve tens of thousands of orbits  

For regional studies, however, the workflow scales well when batching is applied.

---

## 8. Git Workflow

- Created a dedicated issue `hw1_patrick_seidel_sentinel5p_no2` describing the task ✔  
- Regular commits documenting incremental progress ✔  
- Final pull request linked to the issue and containing:
  - this README  
  - the cleaned Jupyter notebook
  - an example report dataframe

---

## 9. References

- Copernicus Data Space Ecosystem: https://dataspace.copernicus.eu/  
- Sentinel Hub Process API: https://documentation.dataspace.copernicus.eu/APIs/SentinelHub/  
- Sentinel-5P $NO_2$ Product: https://sentinels.copernicus.eu/data-products  
- SentinelHub Python package: https://sentinelhub-py.readthedocs.io  


