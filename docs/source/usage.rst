CEDA DataPoint - Basic Usage
============================

This page/notebook demonstrates some basic usage and functionality for
CEDA’s DataPoint package, installable with
``pip install ceda_datapoint``. To begin we can import the datapoint
module and start using the search client.

.. code::

   >>> from ceda_datapoint import DataPointClient
   >>> client = DataPointClient(org='CEDA', hash_token='lonestar')

The hash token and organisation are optional parameters. By default the
organisation will be CEDA and the hash token will be auto-generated to
help the user keep track of ``client``, ``search`` and ``item`` objects
and which are their parent objects. All objects contain a few basic
methods, like ``help`` and ``info`` to get the set of public methods and
some info about the object respectively.

General Info
------------

All ``DataPoint`` objects have some standard methods for retrieving
information, like the ``.help()`` and ``.info()`` methods below. They’re
also all designed for use with a Jupyter notebook, in the way that they
will display information when listed at the end of a cell. See below for
example

.. code::

   >>> # DataPointClient contains a __repr__ method which enables us to do the below:
   >>> client
   <DataPointClient: CEDA-333146>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA

Client and Search
-----------------

As stated above, the client and other objects contain ``help`` and
``info`` methods to print some basic information that might be helpful.


.. code::

   >>> client.info()
   >>> client.help()
   <DataPointClient: CEDA-333146>
    - Client for DataPoint searches via https://api.stac.ceda.ac.uk
   DataPointClient Help:
    > client.info() - Get information about this client.
    > client.list_query_terms() - List of queryable terms for a specific collection
    > client.display_query_terms() - Prints query terms to the terminal.
    > client.list_collections() - Get list of all collections known to this client.
    > client.display_collections() - Print collections and their descriptions
    > client.search() - perform a search operation. For example syntax see the documentation.
   Properties:  id, meta, collection
   See the documentation at https://cedadev.github.io/datapoint/

For the client, we can also get a list of the collections known to the
client under the STAC API, and the queryable terms for each of those
collections. Alternatively these can be displayed by substituting
``list`` for ``display``.


.. code::

   >>> client.list_collections()
   ['cci',
    'cmip6',
    'cordex',
    'eocis-sst-cdrv3',
    'eocis-sst-cdrv3-climatology',
    'land_cover',
    'sentinel1',
    'sentinel2_ard',
    'ukcp']

.. code::

   >>> client.list_query_terms(collection='cmip6')
   ['datetime',
    'start_datetime',
    'end_datetime',
    'access',
    'index_node',
    'latest',
    'pid',
    'replica',
    'retracted',
    'instance_id',
    'citation_url',
    'variable_long_name',
    'variable_units',
    'cf_standard_name',
    'activity_id',
    'data_specs_version',
    'experiment_title',
    'frequency',
    'further_info_url',
    'grid',
    'grid_label',
    'institution_id',
    'mip_era',
    'source_id',
    'source_type',
    'experiment_id',
    'sub_experiment_id',
    'nominal_resolution',
    'table_id',
    'variable_id',
    'variant_label',
    'levels',
    'updated',
    'created']

Now we have some basic information about the collections and their
search terms, we can try searching for some data.

Simple dataset access example
-----------------------------

Here we present a very basic search across the ``cmip6`` STAC collection
which returns 10 items, from which we can pull a specific dataset.


.. code::

   >>> search_basic = client.search(
   >>>     collections=['cmip6'],
   >>>     query=[
   >>>         'experiment_id=ssp585',
   >>>         'activity_id=ScenarioMIP',
   >>>         'institution_id=KIOST',
   >>>     ],
   >>>     max_items = 10
   >>> )
   >>> search_basic
   <DataPointSearch: CEDA-333146-139631 ({'collections': ['cmip6'], 'max_items': 10, 'query': 3})>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}

From our search we can collect the cloud assets into a ``cluster``,
index the cluster to get a specific cloud product, then open that cloud
product into an xarray dataset.


.. code::

   >>> # Collect the cloud products from this search into a single cluster
   >>> cluster = search_basic.collect_cloud_assets()
   >>> product = cluster[2] # Index the cluster to find the 3rd product (Note: you can also use the ID)
   >>> 
   >>> # Note: Here we have used a specific item which is known to exist.
   >>> ds = product.open_dataset()
   >>> ds
   <xarray.Dataset> Size: 76MB
   Dimensions:    (lat: 96, bnds: 2, lon: 192, time: 1032)
   Coordinates:
     * lat        (lat) float64 768B -90.0 -88.11 -86.21 ... 86.21 88.11 90.0
     * lon        (lon) float64 2kB 0.9375 2.812 4.688 6.563 ... 355.3 357.2 359.1
     * time       (time) object 8kB 2015-01-17 12:00:00 ... 2100-12-17 12:00:00
   Dimensions without coordinates: bnds
   Data variables:
       lat_bnds   (lat, bnds) float64 2kB dask.array<chunksize=(96, 2), meta=np.ndarray>
       lon_bnds   (lon, bnds) float64 3kB dask.array<chunksize=(192, 2), meta=np.ndarray>
       time_bnds  (time, bnds) object 17kB dask.array<chunksize=(1, 2), meta=np.ndarray>
       vas        (time, lat, lon) float32 76MB dask.array<chunksize=(1, 96, 192), meta=np.ndarray>
   Attributes: (12/47)
       Conventions:            CF-1.7 CMIP-6.2
       activity_id:            ScenarioMIP
       branch_method:          standard
       branch_time_in_child:   60266.0
       branch_time_in_parent:  60266.0
       cmor_version:           3.5.0
       ...                     ...
       table_id:               Amon
       table_info:             Creation Date:(30 April 2019) MD5:cc2ae51c23960ce...
       title:                  KIOST-ESM output prepared for CMIP6
       tracking_id:            hdl:21.14100/7640f386-9b1b-4803-a489-ab4f524b9eba
       variable_id:            vas
       variant_label:          r1i1p1f1

Alternatively we can open the dataset directly from the search if we
already know the ID of the specific dataset.

.. code::

   >>> ds = search_basic.open_dataset(2)
   >>> ds
   <xarray.Dataset> Size: 76MB
   Dimensions:    (lat: 96, bnds: 2, lon: 192, time: 1032)
   Coordinates:
     * lat        (lat) float64 768B -90.0 -88.11 -86.21 ... 86.21 88.11 90.0
     * lon        (lon) float64 2kB 0.9375 2.812 4.688 6.563 ... 355.3 357.2 359.1
     * time       (time) object 8kB 2015-01-17 12:00:00 ... 2100-12-17 12:00:00
   Dimensions without coordinates: bnds
   Data variables:
       lat_bnds   (lat, bnds) float64 2kB dask.array<chunksize=(96, 2), meta=np.ndarray>
       lon_bnds   (lon, bnds) float64 3kB dask.array<chunksize=(192, 2), meta=np.ndarray>
       time_bnds  (time, bnds) object 17kB dask.array<chunksize=(1, 2), meta=np.ndarray>
       vas        (time, lat, lon) float32 76MB dask.array<chunksize=(1, 96, 192), meta=np.ndarray>
   Attributes: (12/47)
       Conventions:            CF-1.7 CMIP-6.2
       activity_id:            ScenarioMIP
       branch_method:          standard
       branch_time_in_child:   60266.0
       branch_time_in_parent:  60266.0
       cmor_version:           3.5.0
       ...                     ...
       table_id:               Amon
       table_info:             Creation Date:(30 April 2019) MD5:cc2ae51c23960ce...
       title:                  KIOST-ESM output prepared for CMIP6
       tracking_id:            hdl:21.14100/7640f386-9b1b-4803-a489-ab4f524b9eba
       variable_id:            vas
       variant_label:          r1i1p1f1

More about Searches
-------------------

Note: The ``id`` for this search object contains the parent id of the
client (in this case ``333146``) plus an additional 6-digit code for
this search. Child objects of this search will contain both sets of
6-digit ids, plus another one for the child. We can also see the
searched terms in the representation of this object.

.. code::

   >>> search_basic
   <DataPointSearch: CEDA-333146-139631 ({'collections': ['cmip6'], 'max_items': 10, 'query': 3})>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - products: 10

We can again use the standard methods to get some insight into this
object.


.. code::

   >>> search_basic.info()
   >>> search_basic.help()
   <DataPointSearch: CEDA-333146-139631 ({'collections': ['cmip6'], 'max_items': 10, 'query': 3})>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - products: 10
   DataPointSearch Help:
    > search.info() - General information about this search
    > search.collect_cloud_assets() - Collect the cloud products into a `cluster`
    > search.display_assets() - List the names of assets for each item in this search
    > search.display_cloud_assets() - List the cloud format types for each item in this search
   Properties:  id, meta, collection, items, assets
   See the documentation at https://cedadev.github.io/datapoint/

We can try some of these public methods listed via the ``help`` method
for this search.


.. code::

   >>> search_basic.display_assets()
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.tas.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.sfcWind.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsus.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsds.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlus.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlds.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.psl.gr1.v20191106 (Collection: cmip6)>
    - reference_file, data0001
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.prsn.gr1.v20210928 (Collection: cmip6)>
    - reference_file, data0001

Note: The above assets are listed with names as they appear in the STAC
assets list. This does not showcase which assets represent cloud
datasets which can be opened via DataPoint. To see the datasets we can
access, you can use the ``display_cloud_assets`` method:


.. code::

   >>> search_basic.display_cloud_assets()
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.tas.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.sfcWind.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsus.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsds.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlus.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlds.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.psl.gr1.v20191106 (Collection: cmip6)>
    - kerchunk
   <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.prsn.gr1.v20210928 (Collection: cmip6)>
    - kerchunk

So from the above, we can see the 10 items returned by this search all
contain a ``kerchunk`` asset which is one we can use to open the set of
data for the item.

We can get a dictionary of ``DataPointItems`` represented by this search
from the ``items`` property.


.. code::

   >>> search_basic.items
   {'CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106': <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106 (Collection: cmip6)>
     - url: https://api.stac.ceda.ac.uk
     - organisation: CEDA
     - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
     - collection: cmip6
     - item: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
     - assets: 2
     - cloud_assets: 1
     - attributes: 34
     - stac_attributes: 8
    Properties:
     - datetime: 2058-01-01T12:00:00Z
     - start_datetime: 2015-01-17T12:00:00Z
     - end_datetime: 2100-12-17T12:00:00Z
     - access: ['HTTPServer']
     - index_node: None
     - latest: True
     - pid: None
     - replica: False
     - retracted: False
     - instance_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
     - citation_url: http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106.json
     - variable_long_name: Northward Near-Surface Wind
     - variable_units: m s-1
     - cf_standard_name: northward_wind
     - activity_id: ScenarioMIP
     - data_specs_version: 01.00.30
     - experiment_title: update of RCP8.5 based on SSP5
     - frequency: mon
     - further_info_url: https://furtherinfo.es-doc.org/CMIP6.KIOST.KIOST-ESM.ssp585.none.r1i1p1f1
     - grid: atmos data regridded from Cubed-sphere (c48) to 94X192
     - grid_label: gr1
     - institution_id: KIOST
     - mip_era: CMIP6
     - source_id: KIOST-ESM
     - source_type: AGCM
     - experiment_id: ssp585
     - sub_experiment_id: none
     - nominal_resolution: 250 km
     - table_id: Amon
     - variable_id: vas
     - variant_label: r1i1p1f1
     - levels: None
     - updated: 2024-02-20T22:14:50.735178Z
     - created: 2024-02-20T22:14:50.735178Z,
    'CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319': <DataPointItem: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319 (Collection: cmip6)>
     - url: https://api.stac.ceda.ac.uk
     - organisation: CEDA
     - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
     - collection: cmip6
     - item: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319
   ...}

Clustering Datasets
-------------------

We can also specifically select the datasets which can be opened into
something called a ``DataPointCluster`` which is just a grouping of
datasets which are linked in some way (e.g having the same
``institution_id``.) This grouping is entirely arbitrary and is only
used in place of a list of datasets, enabling lazy loading of as many
datasets as is needed.


.. code::

   >>> cluster = search_basic.collect_cloud_assets()

The warning displayed here indicates that one of the items did not have
a dataset that could be opened. This cluster contains the recipes to
open all the cloud datasets of different types.

.. code::

   >>> cluster.info()
   >>> cluster.help()
   <DataPointCluster: CEDA-333146-139631-409864 (Datasets: 10)>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - products: 10
   Products:
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.tas.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.sfcWind.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsus.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsds.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlus.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlds.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.psl.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.prsn.gr1.v20210928-reference_file: kerchunk
   DataPointCluster Help:
    > cluster.info() - basic cluster information
    > cluster.open_dataset(index/id) - open a specific dataset in xarray
   Properties:  id, meta, collection, products
   See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> # Again the cluster has a representation that effectively just calls the `info` method.
   >>> cluster
   <DataPointCluster: CEDA-333146-139631-409864 (Datasets: 10)>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - products: 10
   Products:
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.uas.gr1.v20210319-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.tas.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.sfcWind.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsus.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rsds.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlus.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.rlds.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.psl.gr1.v20191106-reference_file: kerchunk
    - CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.prsn.gr1.v20210928-reference_file: kerchunk

We can obtain the set of ``DataPointCloudProducts`` contained within
this cluster from the ``products`` property, similar to ``items`` in the
search object.


.. code::

   >>> cluster.products
   [<DataPointCloudProduct: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file (Format: kerchunk)>
     - url: https://api.stac.ceda.ac.uk
     - organisation: CEDA
     - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
     - collection: cmip6
     - item: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
     - assets: 2
     - cloud_assets: 1
     - attributes: 34
     - stac_attributes: 8
     - asset_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file
     - cloud_format: kerchunk
    Attributes:
     - datetime: 2058-01-01T12:00:00Z
     - start_datetime: 2015-01-17T12:00:00Z
     - end_datetime: 2100-12-17T12:00:00Z
     - access: ['HTTPServer']
     - index_node: None
     - latest: True
     - pid: None
     - replica: False
     - retracted: False
     - instance_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
     - citation_url: http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106.json
     - variable_long_name: Northward Near-Surface Wind
     - variable_units: m s-1
     - cf_standard_name: northward_wind
     - activity_id: ScenarioMIP
     - data_specs_version: 01.00.30
     - experiment_title: update of RCP8.5 based on SSP5
     - frequency: mon
     - further_info_url: https://furtherinfo.es-doc.org/CMIP6.KIOST.KIOST-ESM.ssp585.none.r1i1p1f1
     - grid: atmos data regridded from Cubed-sphere (c48) to 94X192
     - grid_label: gr1
     - institution_id: KIOST
     - mip_era: CMIP6
     - source_id: KIOST-ESM
     - source_type: AGCM
     - experiment_id: ssp585
     - sub_experiment_id: none
     - nominal_resolution: 250 km
     - table_id: Amon
     - variable_id: vas
     - variant_label: r1i1p1f1
     - levels: None
     - updated: 2024-02-20T22:14:50.735178Z
     - created: 2024-02-20T22:14:50.735178Z,
   ...]

Getting Datasets - Cloud Products
---------------------------------

We can select a specific ``CloudProduct`` from the cluster simply by
indexing the cluster, or selecting the ID (which can be seen from the
representation above):


.. code::

   >>> cloud1 = cluster['CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file']
   >>> cloud1
   <DataPointCloudProduct: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file (Format: kerchunk)>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - collection: cmip6
    - item: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
    - assets: 2
    - cloud_assets: 1
    - attributes: 34
    - stac_attributes: 8
    - asset_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file
    - cloud_format: kerchunk
   Attributes:
    - datetime: 2058-01-01T12:00:00Z
    - start_datetime: 2015-01-17T12:00:00Z
    - end_datetime: 2100-12-17T12:00:00Z
    - access: ['HTTPServer']
    - index_node: None
    - latest: True
    - pid: None
    - replica: False
    - retracted: False
    - instance_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
    - citation_url: http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106.json
    - variable_long_name: Northward Near-Surface Wind
    - variable_units: m s-1
    - cf_standard_name: northward_wind
    - activity_id: ScenarioMIP
    - data_specs_version: 01.00.30
    - experiment_title: update of RCP8.5 based on SSP5
    - frequency: mon
    - further_info_url: https://furtherinfo.es-doc.org/CMIP6.KIOST.KIOST-ESM.ssp585.none.r1i1p1f1
    - grid: atmos data regridded from Cubed-sphere (c48) to 94X192
    - grid_label: gr1
    - institution_id: KIOST
    - mip_era: CMIP6
    - source_id: KIOST-ESM
    - source_type: AGCM
    - experiment_id: ssp585
    - sub_experiment_id: none
    - nominal_resolution: 250 km
    - table_id: Amon
    - variable_id: vas
    - variant_label: r1i1p1f1
    - levels: None
    - updated: 2024-02-20T22:14:50.735178Z
    - created: 2024-02-20T22:14:50.735178Z

The ``CloudProduct`` object wraps a single dataset meaning we don’t have
to load the data file into xarray until needed. We can get some
information from the STAC index about this product from this object,
including all the attributes belonging to the parent Item.


.. code::

   >>> cloud1.info()
   >>> cloud1.help()
   <DataPointCloudProduct: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file (Format: kerchunk)>
    - url: https://api.stac.ceda.ac.uk
    - organisation: CEDA
    - search_terms: {'collections': ['cmip6'], 'query': ['experiment_id=ssp585', 'activity_id=ScenarioMIP', 'institution_id=KIOST'], 'max_items': 10}
    - collection: cmip6
    - item: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
    - assets: 2
    - cloud_assets: 1
    - attributes: 34
    - stac_attributes: 8
    - asset_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106-reference_file
    - cloud_format: kerchunk
   Attributes:
    - datetime: 2058-01-01T12:00:00Z
    - start_datetime: 2015-01-17T12:00:00Z
    - end_datetime: 2100-12-17T12:00:00Z
    - access: ['HTTPServer']
    - index_node: None
    - latest: True
    - pid: None
    - replica: False
    - retracted: False
    - instance_id: CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106
    - citation_url: http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106.json
    - variable_long_name: Northward Near-Surface Wind
    - variable_units: m s-1
    - cf_standard_name: northward_wind
    - activity_id: ScenarioMIP
    - data_specs_version: 01.00.30
    - experiment_title: update of RCP8.5 based on SSP5
    - frequency: mon
    - further_info_url: https://furtherinfo.es-doc.org/CMIP6.KIOST.KIOST-ESM.ssp585.none.r1i1p1f1
    - grid: atmos data regridded from Cubed-sphere (c48) to 94X192
    - grid_label: gr1
    - institution_id: KIOST
    - mip_era: CMIP6
    - source_id: KIOST-ESM
    - source_type: AGCM
    - experiment_id: ssp585
    - sub_experiment_id: none
    - nominal_resolution: 250 km
    - table_id: Amon
    - variable_id: vas
    - variant_label: r1i1p1f1
    - levels: None
    - updated: 2024-02-20T22:14:50.735178Z
    - created: 2024-02-20T22:14:50.735178Z
   DataPointCloudProduct Help:
    > product.info() - Get information about this cloud product.
    > product.open_dataset() - Open the dataset for this cloud product (in xarray)
   Properties:  id, meta, collection, href, cloud_format, bbox, start_datetime, end_datetime, attributes, stac_attributes, variables, units
   See the documentation at https://cedadev.github.io/datapoint/

.. code::

   >>> cloud1.attributes
   {'datetime': '2058-01-01T12:00:00Z',
    'start_datetime': '2015-01-17T12:00:00Z',
    'end_datetime': '2100-12-17T12:00:00Z',
    'access': ['HTTPServer'],
    'index_node': None,
    'latest': True,
    'pid': None,
    'replica': False,
    'retracted': False,
    'instance_id': 'CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106',
    'citation_url': 'http://cera-www.dkrz.de/WDCC/meta/CMIP6/CMIP6.ScenarioMIP.KIOST.KIOST-ESM.ssp585.r1i1p1f1.Amon.vas.gr1.v20191106.json',
    'variable_long_name': 'Northward Near-Surface Wind',
    'variable_units': 'm s-1',
    'cf_standard_name': 'northward_wind',
    'activity_id': 'ScenarioMIP',
    'data_specs_version': '01.00.30',
    'experiment_title': 'update of RCP8.5 based on SSP5',
    'frequency': 'mon',
    'further_info_url': 'https://furtherinfo.es-doc.org/CMIP6.KIOST.KIOST-ESM.ssp585.none.r1i1p1f1',
    'grid': 'atmos data regridded from Cubed-sphere (c48) to 94X192',
    'grid_label': 'gr1',
    'institution_id': 'KIOST',
    'mip_era': 'CMIP6',
    'source_id': 'KIOST-ESM',
    'source_type': 'AGCM',
    'experiment_id': 'ssp585',
    'sub_experiment_id': 'none',
    'nominal_resolution': '250 km',
    'table_id': 'Amon',
    'variable_id': 'vas',
    'variant_label': 'r1i1p1f1',
    'levels': None,
    'updated': '2024-02-20T22:14:50.735178Z',
    'created': '2024-02-20T22:14:50.735178Z'}

We can now use the ``open_dataset`` method of this cloud product to
obtain an Xarray representation of the data. In the future it will be
possible to get a cf-python representation instead, but this is not yet
implemented.


.. code::

   >>> ds = cloud1.open_dataset()
   >>> print(ds)
   <xarray.Dataset> Size: 76MB
   Dimensions:    (lat: 96, bnds: 2, lon: 192, time: 1032)
   Coordinates:
     * lat        (lat) float64 768B -90.0 -88.11 -86.21 ... 86.21 88.11 90.0
     * lon        (lon) float64 2kB 0.9375 2.812 4.688 6.563 ... 355.3 357.2 359.1
     * time       (time) object 8kB 2015-01-17 12:00:00 ... 2100-12-17 12:00:00
   Dimensions without coordinates: bnds
   Data variables:
       lat_bnds   (lat, bnds) float64 2kB dask.array<chunksize=(96, 2), meta=np.ndarray>
       lon_bnds   (lon, bnds) float64 3kB dask.array<chunksize=(192, 2), meta=np.ndarray>
       time_bnds  (time, bnds) object 17kB dask.array<chunksize=(1, 2), meta=np.ndarray>
       vas        (time, lat, lon) float32 76MB dask.array<chunksize=(1, 96, 192), meta=np.ndarray>
   Attributes: (12/47)
       Conventions:            CF-1.7 CMIP-6.2
       activity_id:            ScenarioMIP
       branch_method:          standard
       branch_time_in_child:   60266.0
       branch_time_in_parent:  60266.0
       cmor_version:           3.5.0
       ...                     ...
       table_id:               Amon
       table_info:             Creation Date:(30 April 2019) MD5:cc2ae51c23960ce...
       title:                  KIOST-ESM output prepared for CMIP6
       tracking_id:            hdl:21.14100/7640f386-9b1b-4803-a489-ab4f524b9eba
       variable_id:            vas
       variant_label:          r1i1p1f1

From this point we are dealing with a single specific Xarray Dataset
object, meaning all standard xarray methods can be applied. For help
with using Xarray datasets, see the xarray documentation at
https://docs.xarray.dev/en/stable/.