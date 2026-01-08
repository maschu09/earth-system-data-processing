# Pipeline Architecture & Flow Diagram

## Control Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    era5_pipeline.py                             │
│              (Main Control Flow Script)                         │
└────────────────────┬────────────────────────────────────────────┘
                     │
         ┌───────────┴──────────────┬──────────┬────────────┐
         │                          │          │            │
      [DATE]                    [--start]  [--end]     [--mock]
         │                          │          │            │
         ▼                          ▼          ▼            ▼
    ┌────────────┐          ┌────────────┐  [Toggle]  [Test Mode]
    │Single Date │          │Date Range  │     │         │
    └────┬───────┘          └────┬───────┘     │         │
         │                       │             │         │
         └───────────┬───────────┘             │         │
                     │                        │         │
                     ▼                        ▼         ▼
         ┌──────────────────────────────────────────────────┐
         │      Auto-Detect Missing Files?                 │
         │   (find_oldest_missing_file)                    │
         └──────────────────┬───────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         ┌─────────────────┐    ┌──────────────┐
         │ Files Found     │    │No Files      │
         │Process Range    │    │Stop          │
         └────────┬────────┘    └──────────────┘
                  │
                  ▼
    ┌─────────────────────────────────────────┐
    │   For Each Date in Range:               │
    │                                         │
    │  1. Download ERA5 Data                  │
    │     (download_era5_daily)               │
    │           ↓                             │
    │  2. Process Data                        │
    │     (process_daily_data)                │
    │           ↓                             │
    │  3. Archive Data                        │
    │     (archive_file)                      │
    │                                         │
    │  [MOCK MODE: Skip step 1]               │
    └──────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────────┐
         │  Log Results        │
         │  Success/Failures   │
         └─────────────────────┘
```

---

## Module Architecture

```
                      ┌─────────────────────┐
                      │   config.py         │
                      │ (User Settings)     │
                      │                     │
                      │ - variable          │
                      │ - pressure_levels   │
                      │ - times             │
                      │ - format            │
                      │ - grid              │
                      │ - date_range        │
                      └────────┬────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
    ┌──────────────────┐ ┌────────────┐ ┌──────────────┐
    │  download.py     │ │processing. │ │era5_pipeline │
    │                  │ │     py     │ │      .py     │
    │ • CDS API calls  │ │            │ │              │
    │ • File download  │ │ • Process  │ │ • Orchestrate│
    │ • Error handling │ │   data     │ │ • Date logic │
    │ • File checking  │ │ • Archive  │ │ • CLI args   │
    │                  │ │   files    │ │              │
    └────────┬─────────┘ └──────┬─────┘ └──────┬───────┘
             │                  │              │
             │    ┌─────────────┴──────────────┘
             │    │
             ▼    ▼
         ┌─────────────────────┐
         │  Logging System     │
         │                     │
         │ • pipeline.log      │
         │ • download.log      │
         │ • processing.log    │
         └─────────────────────┘
```

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    COPERNICUS CDS                            │
│            (ERA5 Climate Data Store)                         │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 │ download_era5_daily()
                 │
                 ▼
    ┌────────────────────────────┐
    │  data/era5/                │
    │                            │
    │ era5_relative_humidity_    │
    │    20241201.nc   ✓         │
    │    20241202.nc   ✓         │
    │    20241203.nc   ✓         │
    │    20241204.nc   ✓         │
    │    20241205.nc   ✓         │
    │                            │
    └────────────┬───────────────┘
                 │
                 │ process_daily_data()
                 │
                 ▼
    ┌────────────────────────────┐
    │  processed/era5/           │
    │                            │
    │ processed_era5_relative_   │
    │    humidity_20241201.nc ✓  │
    │    humidity_20241202.nc ✓  │
    │    humidity_20241203.nc ✓  │
    │    humidity_20241204.nc ✓  │
    │    humidity_20241205.nc ✓  │
    │                            │
    └────────────┬───────────────┘
                 │
                 │ archive_file()
                 │
                 ▼
    ┌────────────────────────────┐
    │  archive/era5/             │
    │  └─ 2024/                  │
    │     └─ 12/                 │
    │        ├─ processed_..01.nc│
    │        ├─ processed_..02.nc│
    │        ├─ processed_..03.nc│
    │        ├─ processed_..04.nc│
    │        └─ processed_..05.nc│
    │                            │
    └────────────────────────────┘
```

---

## Invocation Modes

```
┌─────────────────────────────────────────────────────────────┐
│              Command Line Invocation                        │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
    ┌───────────┐     ┌──────────┐    ┌──────────────┐
    │ [DATE]    │     │ [--start │    │ [--mock]     │
    │           │     │  --end]  │    │              │
    │ Process   │     │          │    │ Test without │
    │ specific  │     │ Range    │    │ downloading  │
    │ date only │     │ mode     │    │              │
    └─────┬─────┘     └────┬─────┘    └────────┬─────┘
          │                │                   │
          │ ┌──────────────┴───────┐           │
          │ │                      │           │
          └►│ Find Missing        │           │
            │ If no dates given   │◄──────────┘
            │                      │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Process Date Range   │
            │                      │
            │ ├─ Download Step     │
            │ ├─ Process Step      │
            │ └─ Archive Step      │
            │                      │
            │ [Skip download       │
            │  if --mock]          │
            └──────────────────────┘
```

---

## Configuration Influence

```
                    config.py
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    ERA5_CONFIG   DEFAULT_DATES    PATHS
        │               │               │
        │       ┌───────┘               │
        │       │                       │
        │   ┌─►├─────────────┐          │
        │   │  │start_date   │          │
        │   │  │end_date     │          │
        │   │  └─────────────┘          │
        │   │                           │
        └─►├─ variable              ◄───┘
            ├─ pressure_levels
            ├─ times
            ├─ format
            ├─ grid
            │
            └─► download_era5_daily()
                    │
                    ▼
            (Customizable Parameters)
```

---

## Error Handling & Resilience

```
                    Start Processing
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             │
              Process Date    Continue
                    │             │
        ┌───────────┴─────────┐   │
        │                     │   │
        ▼                     ▼   │
    ┌─────────┐          ┌────────┴───┐
    │Download │──Error──►│Log Error    │
    │ Failed? │          │Skip Date    │
    └────┬────┘          │Continue Next│
         │ Success       └─────┬───────┘
         │                     │
         ▼                     │
    ┌─────────┐                │
    │ Process │──Error────┐    │
    │ Failed? │           │    │
    └────┬────┘      ┌────►├───┘
         │ Success   │     │
         │           ▼     │
         │        ┌──────────┐
         │        │Log Error │
         │        │Skip Date │
         │        │Continue  │
         │        └────┬─────┘
         │             │
         └─────┬───────┘
               │
               ▼
        ┌────────────────┐
        │ All Dates      │
        │ Processed      │
        │ Log Summary    │
        └────────────────┘
```

---

## Mock Processing Flow

```
                    --mock flag
                        │
                        ▼
            ┌──────────────────────┐
            │  Download Step       │
            │                      │
            │  Skip CDS API call   │
            │  Create mock file    │
            │  (empty .nc file)    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Processing Step     │
            │                      │
            │  Copy file (same)    │
            │  Log as processed    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Archiving Step      │
            │                      │
            │  Move to archive     │
            │  Organize by date    │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Result              │
            │                      │
            │  Full workflow       │
            │  tested in ~1 sec    │
            │  No real download    │
            └──────────────────────┘
```

---

## Configuration Customization Example

```
BEFORE (Default):
    config.py
    ├─ variable: "relative_humidity"
    ├─ pressure_levels: [975, 900, 800, 500, 300]
    ├─ times: ["00:00", "06:00", "12:00", "18:00"]
    ├─ format: "netcdf"
    └─ grid: None

AFTER (Customized):
    config.py
    ├─ variable: "temperature"          ← Changed
    ├─ pressure_levels: [850, 700, 500] ← Changed
    ├─ times: ["00:00", "12:00"]        ← Changed
    ├─ format: "grib"                   ← Changed
    └─ grid: [1.0, 1.0]                 ← Changed

Result:
    Same pipeline code works with completely different data!
```

---

## Summary

- **Single command** triggers complete workflow
- **Modular design** allows independent function use
- **Smart date handling** auto-detects missing files
- **Configuration external** (no hardcoding)
- **Error resilient** (continues on failures)
- **Fully logged** (comprehensive operation tracking)
- **Mock testable** (validate workflow without data)
- **Production ready** (tested and documented)
