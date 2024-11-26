=============
Cloud Formats
=============

From recent user surveys relating to the Climate Model Intercomparison Project (CMIP6) 
datasets available via the CEDA Archive, some common issues and barriers to research are 
reported. Research in fields such as Atmospheric Chemistry/Dynamics and Climate Model 
Development is done by either connecting to JASMIN using remote SSH or downloading 
entire datasets to local institutions for data analysis. The download process can 
take weeks for some datasets, and not all institutions are able to provide remote JASMIN access. 
To give data users alternative ways of accessing data without requiring large downloads of data, 
cloud-accessible methods of data aggregation must be explored.

Cloud optimisation typically involves breaking up the existing data structure into easy-to-manage data ``chunks``
which can then be requested individually, so if a user would like to utilise only a specific subset of data, 
they only need to access the relevant parts. The chunk structure therefore directly affects performance, and 
special consideration must be given to the size and shapes of chunks diven the end use-case. For example, if all
users are likely to look at regions no smaller than a single country, your chunk sizes should be at least as small,
if not smaller. If the chunk structure is much larger than the area of interest, the user is forced to download a large
set of data, only to discard most of it to then access their small area.

There are generally two approaches with allowing individual chunk access to data: 
 - reformat: break them up into separate objects that can be individually requested.
 - reference: provide a mechanism to get a specific byte range corresponding to that chunk from a larger object. 
The most common formats for utilising these methods (for raster data) are Zarr and Kerchunk respectively. 

.. image:: _images/ChunksPerFileDiagram.png
   :alt: Diagram of when to use specific optimised formats based on chunk structure.

The above diagram demonstrates when is appropriate to use both optimisation methods. Since the reference method does not involve
changing the original chunk structure, it is best to use when there is a high level of chunking already present, 
which can easily be mapped. There are two competing formats to store the references, both used by Kerchunk, depending on how many
references your dataset will produce.

If the source files are not well chunked for the use case or have very few chunks in general, the best solution is reformatting 
to a format like Zarr, which will allow the chunk structure to be altered.

1. Kerchunk Reference format
----------------------------
Kerchunk was developed by Martin Durant at Anaconda as a python library for cloud-friendly access 
to archival data by reference, an alternative to converting archival data into newer cloud-optimised formats. 
There are specific similarities in syntax between Kerchunk and Zarr as there is a significant overlap 
between the teams working on both. The key difference with Kerchunk is that the data is not converted 
or transformed, instead a kerchunk reference file is created which acts as an interface to archived 
NetCDF data. NetCDF files contain encoded data with embedded metadata, shown in Figure. 
Byte-range requests are supported but without opening the file first, the locations of data 
chunks are unknown. The Kerchunk process maps out all chunks within each file in a dataset and 
creates a list of chunk locations and sizes, producing a JSON file which can then be used to make 
range requests. 

.. image:: _images/KerchunkDiagram.png
   :alt: Diagram for accessing an archive via a Kerchunk reference file.

Since Kerchunk files can be opened using Xarray the chunks can be loaded when 
required rather than all at once, a process called Lazy Loading. This removes the requirement 
of downloading an entire NetCDF file to determine which parts of the data are required. In 
that way Kerchunk does part of the work of Zarr, but without the second step of physically 
moving the data into separate containers. Any kerchunk user can use HTTP GET requests to 
retrieve specific byte-ranges of data served by NginX/Apache web-servers which are 
then combined into a single Xarray dataset object. 

2. Zarr stores
--------------

One solution to the problems NetCDF presents in terms of cloud access issues, would be to migrate 
data to a more cloud-friendly format and upload this new format to a public cloud platform like 
Amazon S3 or GCP. These use an Object Store architecture in place of a traditional file system. 
In object storage, items are collected in a flat hierarchy of buckets, with bytes read and written 
within the buckets by http calls. There are several cloud-optimised file formats in development, 
with many organisations starting to implement new storages in these formats and enabling cloud access.

Both Cloud Optimised GeoTIFFs (COG) and Zarr Stores break up existing NetCDF data into chunks which 
enable HTTP requests for efficient dataset slicing and extraction of only the required data chunks. 
Kerchunk originated as a direct alternative to Zarr with many similarities.

.. image:: _images/ZarrDiagram.png
   :alt: Diagram for accessing Zarr store data which has been created from a source.

Zarr is an open-source specification format for storing N-dimensional arrays that may be 
chunked and compressed. Chunks are stored in separate compressed files within a 
Zarr (object), along with separated metadata files (Zarray and Zattrs) as shown in Figure, which 
allows selection and usage of only specific parts of the data. This is useful for large datasets with
multiple variables as only a handful of chunk files need to be accessed for a typical time-series 
slice of multiple variables, whereas doing the same with NetCDF would involve accessing many if 
not all the files and require downloading the full dataset or access to JASMIN.


The JSON-style metadata is stored alongside the binary chunk data in the bucket. Each chunk 
is named using the index position within the N-dimensional chunking regime of the Zarr data 
and is stored as an independent object, hence parallel reads of different Zarr chunks is 
supported. Data can be rechunked on conversion to Zarr to suit operational needs and typical use-cases.

3. Climate Forecast Aggregations (CFA)
--------------------------------------

CFA parameters are now included in the CF conventions (as of CF version 1.12), 
and define how so-called ``aggregation variables`` should be defined within a CFA-netCDF file. A 
CFA-netCDF file acts as a reference file to a set of Fragment files (which may be netCDF or other formats), 
and an appropriate application reader (like cfapyx) is able to read and interpret the aggregated data into 
the proper set of variables and dimensions that cover the extent of the set of Fragment files. Accessing a 
subset of the data is then made more efficient as the application reader can fetch only the portions of the 
array required by the user for any particular computation.