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

**v0.5.0**: (09/06/25) Newly released Single-Search Selections, designed to minimise configuration complexity by applying pystac search parameters directly to the data!

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
