__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import pystac_client
from pystac_client.stac_api_io import StacApiIO
import logging
import hashlib

from ceda_datapoint.mixins import UIMixin
from .cloud import DataPointCluster
from .item import DataPointItem
from .utils import urls, hash_id, generate_id

logger = logging.getLogger(__name__)

class DataPointSearch(UIMixin):
    """
    Search instance created upon searching using the client."""

    def __init__(
            self, 
            pystac_search: object, 
            search_terms: dict = None, 
            meta: dict = None,
            parent_id: str = None
        ):

        self._search_terms = search_terms or None
        self._meta = meta or None

        self._search = pystac_search
        self._item_set  = None

        self._meta['search_terms'] = self._search_terms

        self._id = f'{parent_id}-{hash_id(parent_id)}'

    def __str__(self) -> str:
        """
        String representation of this search.
        """

        terms = {k: v for k, v in self._search_terms.items() if k != 'query'}

        if 'query' in self._search_terms:
            terms['query'] = len(self._search_terms['query'])
        return f'<DataPointSearch: {self._id} ({terms})>'
    
    def __getitem__(self, index) -> DataPointItem:
        """
        Public method to index the dict of items.
        """

        if not self._item_set:
            self._load_item_set()

        if isinstance(index, str):
            if index not in self._item_set:
                logger.warning(
                    f'Item "{index}" not present in the set of items.'
                )
                return None
            return self._item_set[index]
        elif isinstance(index, int):
            if index > len(self._item_set.keys()):
                logger.warning(
                    f'Could not return item "{index}" from the set '
                    f'of {len(self._item_set)} items.'
                )
                return None
            key = list(self._item_set.keys())[index]
            return self._item_set[key]
        else:
            logger.warning(
                f'Unrecognised index type for {index} - '
                f'must be one of ("int","str")'
            )
            return None

    def help(self):
        print('DataPointSearch Help:')
        print(' > search.get_items() - fetch the set of items as a list of DataPointItems')
        print(' > search.info() - General information about this search')
        print(' > search.open_cluster() - Open cloud datasets represented in this search')
        print(' > search.display_assets() - List the names of assets for each item in this search')
        print(' > search.display_cloud_assets() - List the cloud format types for each item in this search')
        super().help()

    def get_items(self) -> dict:
        """
        Public method to get the set of 
        DataPointItem objects.
        """

        if not self._item_set:
            self._load_item_set()

        return self._item_set

    def info(self) -> None:
        """
        Provide information about this search
        """
        print(self)
        print('Search terms:')
        for term, searched in self._search_terms.items():
            print(f' - {term}: {searched}')

    def collect_cloud_assets(
            self,
            mode='xarray',
            combine=False,
            priority=[],
            **kwargs,
        ) -> DataPointCluster:

        """
        Open a DataPointCluster object from the cloud assets for 
        each item in this search.
        """

        if combine:
            raise NotImplementedError(
                '"Combine" feature has not yet been implemented'
            )
        
        if not self._item_set:
            self._load_item_set()
        
        assets = []
        for item in self._item_set.values():
            assets.append(item.get_cloud_assets(priority=priority))

        return DataPointCluster(assets, meta=self._meta, parent_id=self._id)
    
    def display_assets(self) -> None:
        """
        Display the number of assets attributed to each item in
        the itemset.
        """
        if not self._item_set:
            self._load_item_set()

        for item in self._item_set.values():
            assets = item.get_assets()
            print(item)
            print(' - ' + ', '.join(assets.keys()))

    def display_cloud_assets(self) -> None:
        """
        Display the cloud assets attributed to each item in
        the itemset.
        """
        if not self._item_set:
            self._load_item_set()

        for item in self._item_set.values():
            assets = item.list_cloud_formats()
            if not assets:
                print(item)
                print(' <No Cloud Assets>')
            else:
                print(item)
                print(' - ' + ', '.join(assets))

    def _load_item_set(self) -> None:
        """
        Load the set of items for this search into 
        self-describing DataPointItem instances.
        """
        items = {}
        for item in self._search.items():
            items[item.id] = DataPointItem(item, meta=self._meta)
        self._item_set = items
    
class DataPointClient(UIMixin):
    """
    Client for searching STAC collections, returns self-describing 
    components at all points."""

    def __init__(
            self, 
            org: str = 'CEDA', 
            url: str = None,
            hash_token: str = None,
        ) -> None:

        if hash_token is None:
            hash_token = generate_id()

        self._url = url

        if url and org != 'CEDA':
            self._org = org
        elif url:
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

        if self._url is None:
            raise ValueError(
                'API URL could not be resolved'
            )

        self._client = pystac_client.Client.open(self._url)

        self._meta = {
            'url' : self._url,
            'organisation': self._org
        }

        self._id = self._org or ''
        self._id += f'-{hash_id(hash_token)}'

    def __str__(self) -> str:
        """
        String representation of this class.
        """
        org = ''
        if self._org:
            org = f'{self._org}'

        return f'<DataPointClient: {self._id}>'
    
    def help(self):
        print('DataPointClient Help:')
        print(' > client.info() - Get information about this client.')
        print(
            ' > client.list_query_terms() - List terms available to '
            'query for all or a specific collection')
        print(' > client.list_collections() - List all collections known to this client.')
        print(' > client.search() - perform a search operation. For example syntax see the documentation.')
        super().help()

    def info(self):
        print(f'{str(self)}')
        print(f' - Client for DataPoint searches via {self._url}')

    def __getitem__(self, collection):
        """
        Public method for getting a collection from this client
        """
        return DataPointSearch(self.search(collections=[collection]))
        
    def list_query_terms(self, collection=None) -> dict | None:
        """
        List the possible query terms for all or
        a particular collection.
        """

        def search_terms(search, coll, display : bool = False):

            
            item = search[0]
            if item is not None:
                if display:
                    print(f'{coll}: {list(item.attributes.keys())}')
                return { coll : list(item.attributes.keys())}
            else:
                if display:
                    print(f'{coll}: < No Items >')
                return {coll : None}

        if collection is not None:
            dps = self.search(collections=[collection], max_items=1)
            return search_terms(dps, collection)

        else:
            for coll in self._client.get_collections():
                c = self.search(collections=[coll.id], max_items=1)
                _ = search_terms(c, coll.id, display=True)
            return

    def list_collections(self):
        """
        Return a list of the names of collections for this Client
        """
        for coll in self._client.get_collections():
            print(f"{coll.id}: {coll.description}")

    def search(self, **kwargs) -> DataPointSearch:
        """
        Perform a search operation, creates a ``DataPointSearch``
        object which is also self-describing."""
        
        search = self._client.search(**kwargs)
        return DataPointSearch(search, search_terms=kwargs, meta=self._meta, parent_id=self._id)

