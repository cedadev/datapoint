# DataPoint package

**ceda-datapoint** is a Python package which provides Python-based search/access tools for using data primarily from the CEDA Archive. For some time we've been generating so-called 
Cloud Formats which act as representations, references or mappers to data stored in the CEDA Archive. Most of our data is in archival formats like NetCDF/HDF which makes them great for use with the HPC architecture on which the archive resides (see the [JASMIN homepage](https://jasmin.ac.uk/) for more details), but not so good for open access outside of JASMIN. 

See the documentation at https://cedadev.github.io/datapoint for more information.

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