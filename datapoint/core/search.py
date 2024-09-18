__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

from datapoint.stac import DataPointItem
from datapoint.dataset import DataPointCluster

class DataPointSearch:

    def __init__(self, pystac_search, **kwargs):

        self._search = pystac_search

    def __str__(self):
        return '<DataPointSearch>'
    
    def __repr__(self):
        return '\n'.join(
            [str(self)] + [str(self._search.items())]
        )
    
    def get_spatial_extent(self):
        pass

    def get_temporal_extent(self):
        pass

    def get_dimension_info(self):
        pass

    def item_collections(self):
        pass

    def get_items(self):
        item_list = []
        for item in self._search.items():
            item_list.append(
                DataPointItem(item)
            )
        return item_list

    def items(self):
        item_list = []
        for item in self._search.items():
            item_list.append(
                DataPointItem(item)
            )
        yield item_list
    
    def to_dataset(
            self,
            mode='xarray',
            combine=False,
            priority=[],
        ):

        dset, ids = [],[]
        for item in self._search.items():
            it = DataPointItem(item)
            ids.append(it.id)
            ds = it.to_dataset(mode=mode, combine=combine, priority=priority)
            dset.append(ds)

        if len(dset) > 1:
            return DataPointCluster(dset, ids)
        if len(dset) == 1:
            return dset[0]
        
        # User warning here if no files are present.
        return []