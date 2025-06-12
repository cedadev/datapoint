.. ceda-datapoint documentation master file, created by
   sphinx-quickstart on Tue Oct 15 15:34:57 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

CEDA DataPoint API
==================

**ceda-datapoint** is a Python package which provides python-based search/access tools for using data primarily from the CEDA Archive. For some time we've been generating so-called 
Cloud Formats which act as representations, references or mappers to data stored in the CEDA Archive. Most of our data is in archival formats like NetCDF/HDF which makes them great for use
with the HPC architecture on which the archive resides (see the `JASMIN homepage <https://jasmin.ac.uk/>`_ for more details), but not so good for open access outside of JASMIN. 

This module serves as an access layer to the CEDA STAC catalogs, where the direct pathways to these cloud formats can be searched and accessed. It is possible to use any STAC API to 
access our collection, but DataPoint is unique in that it is automatically configured to open cloud datasets given the configuration information in the STAC records that are searched.

New for v0.5 - Single-Search Selections
---------------------------------------

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

Read more in the documentation page, under ``Basic Usage >> New Feature: Simple Configuration with Single-Search Selections``

Installation
------------
The datapoint package can be installed via pip, and requires Python 3.8 or later.

.. code::

   >>> pip install ceda-datapoint

See the section on ``Inspiration`` if you would like to learn more about why ``datapoint`` was developed and how it benefits users of CEDA data.

The long term goal is for datapoint to be included in the set of standard packages and libaries for JASMIN, in the ``Jaspy module``.

.. toctree::
   :maxdepth: 1
   :caption: Details:

   Inspiration <inspiration>
   How to Use DataPoint <usage>
   DataPoint's Cloud Product Handler <cloud_formats>
   DataPoint Objects <objects>
   Mappings for Non-CEDA STAC Catalogs <mappers>
   When to Use DataPoint <examples>
   STAC Catalogs Explained <stac>

.. toctree::
   :maxdepth: 1
   :caption: API Reference
   
   Client and Search <core_client>
   STAC Items <core_item>
   Clusters and Cloud Products <core_cloud>
   Mixins <mixins>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
