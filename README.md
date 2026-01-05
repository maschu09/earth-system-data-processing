
# Earth System Data Processing

**Author**: Yeganeh Khabbazian  
**Course**: Earth System Data Processing, University of Cologne, Winter Semester 2025/26

This repository contains homework assignments for the Earth System Data Processing course.

## Homework Assignments

- **[Homework 1: ECMWF AIFS Data Access](data_access/README_ecmwf_aifs.md)** - Download and visualize AIFS forecast data

## Repository Structure

```
data_access/
├── load_ecmwf_aifs.ipynb       # Jupyter notebook for AIFS data download
├── README_ecmwf_aifs.md         # Complete documentation
├── aifs_input_output_fields.png # AIFS model diagram
└── data/                        # Downloaded GRIB2 files
environment.yml                  # Conda environment specification
```

## Setup

```bash
conda env create -f environment.yml
conda activate aifs
jupyter lab
```

## License

See `LICENSE` file for details.
