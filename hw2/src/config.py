
"""
config.py
 
Central place for user-configurable settings.
"""
 
from dataclasses import dataclass
from typing import Tuple
 
 
@dataclass(frozen=True)
class Settings:
    # -------------------------------------------------
    # Date range for the homework (daily workflow)
    # -------------------------------------------------
    start_date: str = "2024-12-01"
    end_date: str   = "2024-12-05"
 
    # -------------------------------------------------
    # Workflow mode
    # -------------------------------------------------
    # True  -> mock downloads (workflow testing)
    # False -> real ERA5 downloads
    use_mock: bool = False
 
    # -------------------------------------------------
    # Mock settings (only used if use_mock=True)
    # -------------------------------------------------
    mock_fail_prob: float = 0.30
 
    # -------------------------------------------------
    # ERA5 download settings (used if use_mock=False)
    # -------------------------------------------------
    era5_product: str = "reanalysis-era5-pressure-levels"
 
    # Variable name as expected by CDS
    era5_variable: str = "specific_humidity"
 
    # Pressure levels in hPa
    era5_pressure_levels: Tuple[int, ...] = (975, 900, 800, 500, 300)
 
    # 6-hourly data
    era5_hours: Tuple[str, ...] = ("00:00", "06:00", "12:00", "18:00")
 
    # Output file format
    era5_format: str = "netcdf"
