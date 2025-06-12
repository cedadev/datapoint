# DataPoint package

[![PyPI version](https://badge.fury.io/py/ceda-datapoint.svg)](https://pypi.python.org/pypi/ceda-datapoint/)

**ceda-datapoint** is a Python package which provides Python-based search/access tools for using data primarily from the CEDA Archive. For some time we've been generating so-called 
Cloud Formats which act as representations, references or mappers to data stored in the CEDA Archive. Most of our data is in archival formats like NetCDF/HDF which makes them great for use with the HPC architecture on which the archive resides (see the [JASMIN homepage](https://jasmin.ac.uk/) for more details), but not so good for open access outside of JASMIN. 

See the documentation at https://cedadev.github.io/datapoint for more information.

## New for v0.5 - Single-Search Selections

With the release of v0.5.0 of `ceda-datapoint`, the new single-search feature is in production! This significantly simplifies the data selection by applying STAC-based search queries to the Xarray datasets as they are accessed. This applies to all datasets returned via the search, so you will only see the data you've actually requested.

Example search
```
>>> client.search(
   collections=['example_collection'], # Any nested collections will now also be searched.
   intersects={
      "type": "Polygon",
      "coordinates": [[[6, 53], [7, 53], [7, 54], [6, 54], [6, 53]]],
   }, # Intersection also applied to xarray Dataset
   datetime='20250101T000000Z/20250102T000000Z',
   query=[
      'experiment_id':'001',
      'variables':['clt','sst']
   ],
   data_selection={
      'variables':['clt','sst'] # Alternative variable search
      'sel':{
         'nv':slice(0,5)
      }
   }
)
```

In this case, the Intersection (Area of Interest), Datetime range, query options and data selection will all be applied to Xarray datasets as they are delivered, which means upon opening a dataset you will receive an xarray representation that takes into account all your search criteria up to this point!

Read more in the documentation page, under `Basic Usage >> New Feature: Simple Configuration with Single-Search Selections`

## Installation

The DataPoint module is now an installable module with pip!
```
pip install ceda-datapoint
```

## Basic usage

See the documentation for a more in-depth description of how to run a search query and access data.
```
from ceda_datapoint import DataPointClient
client = DataPointClient(org='CEDA)
# Continue to perform searches and access data
```
