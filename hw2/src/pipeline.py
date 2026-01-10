
"""
pipeline.py
 
Daily processing pipeline (Homework #2 - control flow requirement).
 
Features:
- Run with no arguments:
    -> find the oldest missing day and process forward day-by-day.
- Run with a date argument YYYY-MM-DD:
    -> process only that specific day.
- Uses a ".done" marker file per day in data/status/ to support restart/resume.
 
This file controls the workflow.
Download method is chosen via Settings.use_mock:
- use_mock=True  -> mock download (for testing)
- use_mock=False -> real ERA5 download (via src/era5_download.py)
"""
 
from __future__ import annotations
 
import sys
import random
from datetime import datetime, date, timedelta
from pathlib import Path
 
from .config import Settings
from .era5_download import Era5Request, download_era5_pressure_levels_day
 
 
# -----------------------------
# Helper functions for dates
# -----------------------------
def parse_day(day_str: str) -> date:
    """Convert 'YYYY-MM-DD' string to a date object."""
    return datetime.strptime(day_str, "%Y-%m-%d").date()
 
 
def day_to_str(d: date) -> str:
    """Convert a date object to 'YYYY-MM-DD' string."""
    return d.strftime("%Y-%m-%d")
 
 
def daterange(start: date, end_inclusive: date):
    """Yield dates from start to end_inclusive (including end_inclusive)."""
    cur = start
    while cur <= end_inclusive:
        yield cur
        cur += timedelta(days=1)
 
 
# -----------------------------
# Resume logic using done markers
# -----------------------------
def status_dir() -> Path:
    """Folder where .done marker files are stored."""
    return Path("data/status")
 
 
def done_marker_path(day: str) -> Path:
    """Path of the .done marker file for a given day."""
    return status_dir() / f"{day}.done"
 
 
def is_done(day: str) -> bool:
    """Return True if day is already processed (marker exists)."""
    return done_marker_path(day).exists()
 
 
def mark_done(day: str) -> None:
    """Create a .done marker file for the day."""
    status_dir().mkdir(parents=True, exist_ok=True)
    done_marker_path(day).write_text("ok\n", encoding="utf-8")
 
 
def find_oldest_missing_day(start: date, end_inclusive: date) -> date | None:
    """
    Find the oldest date in [start, end_inclusive] that is NOT marked done.
    Returns None if all days are done.
    """
    for d in daterange(start, end_inclusive):
        if not is_done(day_to_str(d)):
            return d
    return None
 
 
# -----------------------------
# Download routines
# -----------------------------
def mock_download(day: str, fail_prob: float) -> Path:
    """
    Simulate a download step (for workflow testing):
    - sometimes fails (random)
    - otherwise creates a tiny temp file in data/tmp/
    """
    tmp_dir = Path("data/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
 
    # Random failure for testing the pipeline robustness
    if random.random() < fail_prob:
        raise RuntimeError(f"Mock download failed for {day}")
 
    out_path = tmp_dir / f"{day}.mock.txt"
    out_path.write_text(f"mock data for {day}\n", encoding="utf-8")
    return out_path
 
 
def era5_download(day: str, settings: Settings) -> Path:
    """
    Real ERA5 download for one day.
    The ERA5 settings come from config.py (NOT hardcoded here).
    """
    tmp_dir = Path("data/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
 
    request = Era5Request(
        product=settings.era5_product,
        variable=settings.era5_variable,
        pressure_levels=settings.era5_pressure_levels,
        hours=settings.era5_hours,
        format=settings.era5_format,
    )
 
    out_path = tmp_dir / f"{day}.era5.nc"
    return download_era5_pressure_levels_day(day=day, request=request, out_path=out_path)
 
 
def download_one_day(day: str, settings: Settings) -> Path:
    """
    Choose the download method depending on settings.use_mock.
    """
    if settings.use_mock:
        return mock_download(day, fail_prob=settings.mock_fail_prob)
    else:
        return era5_download(day, settings)
 
 
# -----------------------------
# Daily processing
# -----------------------------
def process_one_day(d: date, settings: Settings) -> None:
    """
    Process one day:
    1) download (mock or real)
    2) placeholder processing (regrid + zarr will be added later)
    3) mark done
    """
    day = day_to_str(d)
    print(f"\n=== Processing {day} ===")
 
    # 1) Download
    try:
        fpath = download_one_day(day, settings)
        print("Download OK ->", fpath)
    except Exception as e:
        # Important: If download fails, we do NOT mark done.
        # This allows the pipeline to retry later.
        print("Download FAILED ->", e)
        return
 
    # 2) Placeholder for next steps:
    # Later: open netCDF -> regrid to healpix -> save to zarr
    print("Processing placeholder OK (regrid + zarr will be added next)")
 
    # 3) Mark done
    mark_done(day)
    print("Marked done ->", done_marker_path(day))
 
 
# -----------------------------
# Main CLI entry point
# -----------------------------
def main(argv: list[str]) -> int:
    """
    Usage:
      python -m src.pipeline
        -> process oldest missing day forward until end_date
 
      python -m src.pipeline YYYY-MM-DD
        -> process only that date
    """
    settings = Settings()
 
    start = parse_day(settings.start_date)
    end = parse_day(settings.end_date)
 
    # Case A: date argument provided
    if len(argv) == 1:
        d = parse_day(argv[0])
        process_one_day(d, settings)
        return 0
 
    # Case B: no args -> process oldest missing forward
    if len(argv) == 0:
        missing = find_oldest_missing_day(start, end)
        if missing is None:
            print("All days are already processed (nothing to do).")
            return 0
 
        for d in daterange(missing, end):
            if is_done(day_to_str(d)):
                continue
            process_one_day(d, settings)
        return 0
 
    # Anything else: print help
    print(main.__doc__)
    return 2
 
 
if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
