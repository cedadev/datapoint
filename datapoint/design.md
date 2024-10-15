## Methods to override for pystac_client

define client -> init in DataPoint defines a client

get_collections -> for each collection define a wrapper DataPointCollection

get_items -> for each item define a wrapper DataPointItem

DataPointCollection.extent.spatial.bboxes -> syntax improvements

DataPointCollection.extent.temporal.intervals -> syntax improvements

DataPointClient.search -> returns a DataPointSearch wrapper

DataPointSearch.items -> for each item define a wrapper DataPointItem

DataPointItem properties dict-like interface?

DataPointSearch url_with_parameters -> syntax improvements?

DataPointSearch.request -> returns a 'response' object

DataPointSearch.matched -> length of items

DataPointItem to_dict -> with properties?

DataPointItem.assets -> dict of DataPointAsset objects?

DataPointItem.to_numpy -> for images etc.

DataPointCloudProduct <- custom object for each cloud product known by the item.


Objects:
 - DataPointClient
 - DataPointSearch
    - DataPointItem
    - DataPointCluster < collection of datasets >

modules:
 - core
   - client
   - search
 - block
   - item
   - asset
 - dataset
   - cloud
   - other? (image, rasterio etc.)



