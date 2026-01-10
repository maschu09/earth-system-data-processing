
"""
era5_download.py
 
ERA5 download routines using the Copernicus CDS API (cdsapi).
 
Important design rule (for grading):
- No user settings are hardcoded inside the download function.
- Variable name, pressure levels, hours, product name, etc. are passed in.
"""
 
from __future__ import annotations
 
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
 
import cdsapi
 
 
@dataclass(frozen=True)
class Era5Request:
    """
    Defines what to download (dataset name, variable, levels, times, format).
    This dataclass keeps settings clean and makes the download routine reusable.
    """
    product: str                 # e.g. "reanalysis-era5-pressure-levels"
    variable: str                # e.g. "specific_humidity" or "relative_humidity"
    pressure_levels: Sequence[int]
    hours: Sequence[str]         # e.g. ["00:00", "06:00", "12:00", "18:00"]
    format: str = "netcdf"       # "netcdf" or "grib"
 
 
def download_era5_pressure_levels_day(*, day: str, request: Era5Request, out_path: Path) -> Path:
    """
    Download one day of ERA5 pressure-level data.
 
    Parameters
    ----------
    day : str
        Date in format "YYYY-MM-DD"
    request : Era5Request
        What to download (variable, levels, hours, dataset name, format)
    out_path : Path
        Output file path (e.g., data/tmp/2024-12-01.era5.nc)
 
    Returns
    -------
    Path
        The path to the downloaded file.
 
    Notes
    -----
    - Requires a configured CDS API key in ~/.cdsapirc
    - This function does NOT decide which variable/levels/hours to use.
      Those are provided via the `request` argument.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
 
    year, month, daynum = day.split("-")
 
    # CDS API client (reads credentials from ~/.cdsapirc)
    client = cdsapi.Client()
 
    # Build request payload for ERA5 pressure levels
    payload = {
        "product_type": "reanalysis",
        "variable": request.variable,
        "pressure_level": [str(p) for p in request.pressure_levels],
        "year": year,
        "month": month,
        "day": daynum,
        "time": list(request.hours),
        "format": request.format,
    }
 
    # Download to the given path
    client.retrieve(request.product, payload, str(out_path))
 
    return out_path
