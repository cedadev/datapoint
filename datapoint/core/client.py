__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import pystac_client
from pystac_client.stac_api_io import StacApiIO

from .cloud import DataPointCluster
from .item import DataPointItem

from .utils import urls

class DataPointClient:

    def __init__(self, org='CEDA', url=None):

        if url and org != 'CEDA':
            # url and org saved
            self._url = url
            self._org = org
        elif url:
            self._url = url
            self._org = None
        else:
            # Not provided a url so just use the org
            if org not in urls:
                raise ValueError(
                    f'Organisation "{org}" not recognised - please select from '
                    f'{list(urls.keys())}'
                )
            self._url = urls[org]
            self._org = org

        self._client = pystac_client.Client.open(url)

        self._meta = {
            'url' : self._url,
            'organisation': self._org
        }

    def __str__(self):
        msg = ''
        if self._org:
            msg = f'{self._org}: '

        return msg + f'Client for DataPoint searches via {self._url}'
    
    def info(self):
        print(self)

    def __getitem__(self, collection):
        """
        Routine for getting a collection from this client
        """
        return DataPointSearch(self.search(collections=[collection]))
        
    def list_search_terms(self, collection=None):

        def search_terms(search, coll):

            print(f'{coll}:')
            items = list(search.items())
            if len(items) > 0:
                print(' - ' + ', '.join(items[0].get_attributes()))
            else:
                print(' < No Items >')

        if collection is not None:
            dps = self.search(collections=[collection], max_items=1)
            search_terms(dps, collection)

        else:
            for coll in self._client.get_collections():
                c = self.search(collections=[coll.id], max_items=1)
                search_terms(c, coll.id)

    def list_collections(self):
        """
        Return a list of the names of collections for this Client
        """
        # Might need a custom Collection class if we want to do anything fancy.
        #return self._client.get_collections(**kwargs)
        for coll in self._client.get_collections():
            print(f"{coll.id}: {coll.description}")

    def search(self, **kwargs):
        
        search = self._client.search(**kwargs)
        return DataPointSearch(search, search_terms=kwargs, meta=self._meta)

class DataPointSearch:

    def __init__(self, pystac_search, search_terms=None, meta=None):

        self._search_terms = search_terms or None
        self._meta = meta or None

        self._search = pystac_search
        self._items  = None

        self._meta['search_terms'] = self._search_terms

    def __str__(self):
        msg = ''
        if self._org:
            msg = f'{self._org}: '

        return msg + f'Client for DataPoint searches via {self._url}'

    def info(self):
        print('Search terms:')
        for term, searched in self._search_terms.items():
            print(f' - {term}: {searched}')
    
    def __getitem__(self, index):
        return self.items()[index]

    def cloud_assets(self, max_items=-1):
        for item in self.items(max_items=max_items):
            assets = item.cloud_assets()
            print(f'{item}: ')
            print(' - ' + ', '.join(assets))

    def _get_items(self):
        item_list = []
        for item in self._search.items():
            item_list.append(DataPointItem(item))
        self._items = item_list

    def items(self, max_items=-1):
        if self._items is None:
            self._get_items()
        return self._items
    
    def open_cluster(
            self,
            mode='xarray',
            combine=False,
            priority=[],
            **kwargs,
        ):

        if combine:
            raise NotImplementedError(
                '"Combine" feature has not yet been implemented'
            )
        
        assets = []
        for item in self.items():
            assets.append(item.get_cloud_assets(priority=priority))

        return DataPointCluster(assets, meta=self._meta)