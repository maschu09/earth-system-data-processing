## Daily Loop

I prepared a script that can be called via the command line. All relevant parameters can be passed when calling the script. To retrieve the data required in the exercise, simply call:

`python daily_processing_era5.py --save_path <your_path> --start_date 2024-12-01 --end_date 2024-12-05`.

To specify the other parameters, use the `--levels`, `--params`, `--shortname` and `--nsides` parameters. For list parameters, supply a space-separated list.

While not explicitly mentioned in the exercise description, I added a start and end date for retrieving data within a specified interval, which is needed for the rest of the task. I thus implemented in the following way:
- start and end date are optional arguments; if no start date is given, the oldest record is used; if no end date is given, the current date is used
- the function then checks the output zarr and looks for any missing dates to fetch between the start and end date - if there are inconsistencies between the dates present for different NSIDE values, these will be mitigated after script execution, making it possible to add different NSIDE values to the same zarr after the initial creation. 

    More formally:

    Assume a zarr store already existis with NSIDE values A, B, C.
    
    - nside A has data for dates [a, b, c, d, e] 
    - nside B has data for dates [a, b, c] 
    - nside C has data for dates [c, d, e] 
    
    The user requests time-interval from a-g, so 
    - for nside A, [f, g] need to be added 
    - nside B, [c, d, e, f, g] need to be added 
    - nside C, [a, b, c, f, g] need to be added

    Thus, only  date c will be ommited from the processing loop. After execution, all NSIDE groups will contain the data for the whole time-interval a-g.

- still possible to pass single date to retrieve data for a single day


## CDS API Request

I used this [page](https://confluence.ecmwf.int/display/UDOC/ENS%3A+Atmospheric+%28enfo%29%2C+Perturbed+Forecast+%28pf%29+for+single+level+%28sfc%29%3A+Guidelines+to+write+efficient+MARS+requests) as reference to construct the required request to the CDS API.:

- Contrary to the example notebook (load_ecmwf_era5.ipynb), we do not need forecasting data, so we load the analysis data `"class": "ea"`.
- As required, we only load single days
- For 6-hourly intervals, we need to define the exact time-points for `"time"` parameter
- the pressure-levels and varaibles are defined flexibly, s.t. any available configuration can be fetched. 
**NOTE**: in the rest of the processing (from netCDF to zarr), I am using the parameter-shortname, which can also be passed to the function. While the retrieval allows for multiple variables, only the variable passed to `param_shortname` will be saved in the .zarr. 
- In the lables listed [here](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation#ERA5:datadocumentation-Table1), the correct IDs and shortnames for the variables can be found. For humidity, the correct identifier is `133.128` and the parameter-shortname is `q`.
- I retrieve the data in netCDF format, which can then easily be loaded using `xarray`.


## Transforming map data to Healpix

To map the data to a healpix grid, I followed the official [tutorial](https://healpy.readthedocs.io/en/latest/tutorial.html). There also exists [another tutorial](https://gist.github.com/zonca/680c68c3d60697eb0cb669cf1b41c324) linked on the official documentation page, specifically meant for transforming map data into healpix data. However, in this toy example, the authors have a much smaller scale origin data, yielding a 1-to-1 mapping between map-values and healpix-grid indices. 

In our case, its not as simple, as we seem to have a N-to-1 relation between map-values and grid-indices, i.e. multiple indices are mapped to the same grid cell. To illustrate, consider we have $N$ data-values that are assigned to a single healpix-cell $c$. If we use the approach from the tutorial, only one of the $N$ values will be assigned to $c$. This might be seen as a random sampling approach, where a single value represents the whole group of $N$ values. However, a more reasonable approach would be to assign the average of all $N$ values to $c$, which is what I chose to implement.

I thus create a single healpix map for every combination of pressure-level, time-step and NSIDE.

## Saving in Zarr format

The Healpix data is written to one Zarr store, with **one group per spatial resolution**:

* `nside=8`
* `nside=16`

Different NSIDE values correspond to different grids and is therefore kept separate. Each group can be loaded independently.

Within each `nside` group, the data is stored as an `xarray.Dataset` with dimensions:

* `time` (6-hourly time steps),
* `level` (pressure levels),
* `pix` (Healpix pixel index).

The data variable (e.g. `q`) has shape `(time, level, pix)`.

**Chunking strategy**

I chose the chunking strategy to match typical access patterns:

* `time: 1` – enables efficient appending and time-based subsetting,
* `level: 1` – allows loading individual pressure levels,
* `pix: -1` – stores the full Healpix map in a single chunk.

This results in chunks of shape `(1, 1, Npix)`, which avoids fragmenting the spatial dimension while keeping temporal and vertical access efficient.

**Appending/Inserting data**

Data is appended to the dataset along the time domain for each NSIDE value. For this to work correctly, the same level configuration needs to be chosen. Note, if the dataset for an arbitrary NSIDE value has gaps (i.e. a day is missing), in the next execution of the script, this day will be processed and appended, but not _inserted_ in the traditional sense. This will result in a possibly unordered time-list within the dataset, which can be easily fixed by sorting this variable when loading the data.
