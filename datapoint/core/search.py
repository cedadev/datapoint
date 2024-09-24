__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

from datapoint.stac import DataPointItem
from datapoint.dataset import DataPointCluster

class DataPointSearch:

    def __init__(self, pystac_search, search_terms=None):

        self._search_terms = search_terms or None

        self._search = pystac_search
        self._items  = None

    def info(self):
        print('Search terms:')
        for term, searched in enumerate(self._search_terms):
            print(f' - {term}: {searched}')
    
    def __getitem__(self, index):
        return self.items()[index]

    def cloud_assets(self, max_items=-1):
        for item in self.items(max_items=max_items):
            assets = item.cloud_assets()
            print(f'{item.id}: ')
            print(' - ' + ', '.join(assets))

    def _get_items(self):
        item_list = []
        for item in self._search.items():
            item_list.append(
                DataPointItem(item)
            )
        self._items = item_list

    def items(self, max_items=-1):
        if self._items is None:
            self._get_items()
        return self._items
    
    def open_dataset(
            self,
            mode='xarray',
            combine=False,
            priority=[],
        ):

        dset, ids = [],[]
        for item in self._search.items():
            it = DataPointItem(item)
            ids.append(it.id)
            ds = it.open_dataset(mode=mode, combine=combine, priority=priority)
            dset.append(ds)

        if len(dset) > 1:
            return DataPointCluster(dset, ids)
        if len(dset) == 1:
            return dset[0]
        
        # User warning here if no files are present.
        return []