=============================
STAC Catalogs and Conventions
=============================

The CEDA STAC catalogs are accessible via an API portal at https://api.ceda.stac.ac.uk.

.. image:: _images/STACLogo.png
   :alt: The Spatio-Temporal Asset Catalog Logo

1. The basics of STAC
---------------------

Spatio-Temporal Asset Catalog is an emerging standard for storing Geospatial assets in JSON-style format, 
with a convention for metadata attributes to be stored so that STAC records are uniform and standardised across institutions and data centers. 
The STAC methodology consists of several hierarchical layers for organising geospatial data such that searching and accessing data are made 
consistent and easy. STAC objects are grouped into three categories, as seen in the figure:

 - STAC Assets: Lowest level object, a single NetCDF file representing some arbitrary N-dimensional data.
 - STAC Items: A grouping of assets that are associated by some attributes. This could be a set of NetCDF files or a Cloud Optimised object like a Zarr Store.
 - STAC Catalog: Access point for Item browsing, all items can be searched via their defined attributes using an API.

Read more about STAC conventions and possible extensions/plugins on the `STAC Docs <https://stacspec.org/en>`_.

2. STAC Conventions from CEDA
-----------------------------

At CEDA we have created multiple STAC Catalogs for various collections of data, all accessible via a single URL - this is what DataPoint uses.
Our convention for storing cloud format records alongside more traditional file types is to create an Item for each dataset object. This item then has one or more
assets; the original data files in NetCDF or similar formats plus a ``reference-file`` asset which is typically a Kerchunk or CFA file. Zarr will likely also fit under
this or perhaps a different keyword asset name. Items may have multiple ``reference-file`` assets, but should not have more than one of the same format. For example an item
can have a Kerchunk and Zarr asset, but should not have two Kerchunk assets since each item should have a one-to-one mapping with a cloud dataset object.

DataPoint can identify the ``reference-file`` assets and check the ``cloud_format`` property if it exists to direct the user as to which format the asset represents. The asset
then contains properties like ``open_zarr_kwargs`` or ``open_mapper_kwargs`` which are used internally to open an xarray dataset object to serve to the user. The actual loading of
the cloud object into a dataset happens as lazily as possible - meaning the data is not accessed until directly requested to preserve memory space in the user's environment for
as long as possible.