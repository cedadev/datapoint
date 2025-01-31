__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging
from typing import Union

import pystac_client
import xarray as xr
from pystac_client.stac_api_io import StacApiIO

from ceda_datapoint.mixins import UIMixin
from ceda_datapoint.utils import generate_id, hash_id, logstream, urls

from .cloud import DataPointCluster, DataPointMapper
from .item import DataPointItem

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class DataPointSearch(UIMixin):
    """
    Search instance created upon searching using the client."""

    def __init__(
            self, 
            pystac_search: object, 
            mappings: dict = None,
            search_terms: dict = None, 
            meta: dict = None,
            parent_id: str = None
        ) -> None:
        """
        Initialise the search object - used by the DataPointClient
        upon searching.
        
        :param pystac_search:   (object) The returned search object from pystac_client (to be abstracted).
        
        :param search_terms:    (dict) The search terms used in the search query.
        
        :param meta:            (dict) Metadata about the Client (url/organisation etc.)

        :param parent_id:       (str) ID of the parent client.
        """

        self._search_terms = search_terms or None
        self._meta = meta or None

        self._mappings = mappings

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

        :param index:       (int|str) The index or ID from which to pull an 
            item from the search.
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

    @property
    def items(self) -> dict[str, DataPointItem]:
        """
        Get the set of ``DataPointItem`` objects 
        described by this search.
        """

        if not self._item_set:
            self._load_item_set()
        return self._item_set

    @property
    def assets(self) -> dict:
        """
        Get the set of assets under each item in
        this search, returned as a set of nested
        dictionaries.
        """

        if not self._asset_set:
            self._load_asset_set()
        return self._asset_set
            
    def help(self) -> None:
        """Helper function - lists methods that can be utilised for this class"""
        print('DataPointSearch Help:')
        print(' > search.info() - General information about this search')
        print(' > search.collect_cloud_assets() - Collect the cloud products into a `cluster`')
        print(' > search.display_assets() - List the names of assets for each item in this search')
        print(' > search.display_cloud_assets() - List the cloud format types for each item in this search')
        super().help(additionals=['items','assets'])
    
    def info(self) -> None:
        """
        Provide information about this search
        """
        print(self.__repr__())

    def open_dataset(
            self,
            id : str,
            mode : str = 'xarray',
            combine: bool = False,
            priority: list[str] = [],
            mappings: dict = None,
            **kwargs,
        ) -> xr.Dataset:
        """Open a dataset directly from the search result
        
        :param id:      (str) The ID or index of the dataset in the resulting cluster.
        
        :param mode:    (str) The type of dataset to be returned, currently only Xarray is supported (0.4.X)
        
        :param combine: (bool) Combine multiple datasets to a single dataset - not implemented (0.4.X)
        
        :param priority: (list) Order by which to open a set of datasets.
        
        """
        return self.collect_cloud_assets(
            mode=mode, 
            combine=combine, 
            priority=priority,
            mappings=mappings).open_dataset(id,**kwargs)

    def collect_cloud_assets(
            self,
            mode: str = 'xarray',
            combine: bool = False,
            priority: list[str] = [],
            show_unreachable: bool = False,
            asset_mappings: dict = None,
            **kwargs,
        ) -> DataPointCluster:

        """
        Open a DataPointCluster object from the cloud assets for 
        each item in this search.

        :param mode:    (str) The type of dataset to be returned, currently only Xarray is supported (0.4.X)
        
        :param combine: (bool) Combine multiple datasets to a single dataset - not implemented (0.4.X)
        
        :param priority: (list) Order by which to open a set of datasets.

        :param show_unreachable: (bool) Show the hidden assets that DataPoint has determined are currently unreachable.
        """

        if combine:
            raise NotImplementedError(
                '"Combine" feature has not yet been implemented'
            )
        
        if not self._item_set:
            self._load_item_set(mappings=self._mappings)
        
        assets = []
        for item in self._item_set.values():
            assets.append(
                item.collect_cloud_assets(
                    priority=priority, 
                    show_unreachable=show_unreachable, 
                    asset_mappings=asset_mappings
                )
            )

        return DataPointCluster(assets, meta=self._meta, parent_id=self._id)
    
    def display_assets(self) -> None:
        """
        Display the number of assets attributed to each item in
        the itemset.
        """

        for item in self.items.values():
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

    def _load_item_set(self, mappings: dict = None) -> None:
        """
        Load the set of items for this search into 
        self-describing DataPointItem instances.
        """

        mappings = mappings or self._mappings

        mapper=None
        if mappings is not None:
            mapper = DataPointMapper(mappings=mappings)

        items = {}
        for item in self._search.items():
            items[item.id] = DataPointItem(item, meta=self._meta, mapper=mapper)
        self._item_set = items
    
    def _load_asset_set(self) -> None:
        """
        Load the set of assets under each item for this 
        search as a dictionary
        """
        assets = {}
        for item in self.items.values():
            assets[item.id] = item.get_assets()
        self._asset_set = assets

class DataPointClient(UIMixin):
    """
    Client for searching STAC collections, returns self-describing 
    components at all points."""

    def __init__(
            self, 
            org: str = 'CEDA', 
            url: str = None,
            hash_token: str = None,
            mappings: dict = None,
        ) -> None:
        """
        Initialise a DataPointClient. Default organisation/url
        corresponds to CEDA from config information. A hash token
        can be provided for setting the ID (mostly for testing).
        
        :param org: (str) Organisation with a known API endpoint.
        
        :param url: (str) Bare API endpoint (outside organisation mapper) to search.
        
        :param hash_token (str) Token to use when generating IDs for client and other objects."""

        if hash_token is None:
            hash_token = generate_id()

        self._url = url

        self._mappings = mappings

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

    def help(self) -> None:
        """Helper function - lists methods that can be utilised for this class"""
        print('DataPointClient Help:')
        print(' > client.info() - Get information about this client.')
        print(' > client.list_query_terms() - List of queryable terms for a specific collection')
        print(' > client.display_query_terms() - Prints query terms to the terminal.')
        print(' > client.list_collections() - Get list of all collections known to this client.')
        print(' > client.display_collections() - Print collections and their descriptions')
        print(' > client.search() - perform a search operation. For example syntax see the documentation.')
        super().help()

    def info(self) -> None:
        """Display information about this class object"""
        print(f'{str(self)}')
        print(f' - Client for DataPoint searches via {self._url}')

    def __getitem__(self, collection: str):
        """
        Public method for getting a collection from this client
        """
        return DataPointSearch(self.search(collections=[collection]))
        
    def list_query_terms(self, collection: str) -> Union[list,None]:
        """
        List the possible query terms for all or
        a particular collection.
        """
        dps = self.search(collections=[collection], max_items=1)
        item = dps[0]
        if item is not None:
            return list(item.attributes.keys())
        else:
            logger.warning(f'Collection {collection} returned no search terms.')
            return None
        
    def display_query_terms(self, collection: str = None) -> None:
        """
        Display query terms for all collections or 
        just a specific collection.
        """
        colls = self.list_collections()
        if collection is not None:
            if collection in colls:
                print(f'{collection}: {self.list_query_terms(collection)}')
            else:
                logger.warning(f'Collection {collection} was not found.')
            return
        
        for coll in colls:
            print(f'{coll}: {self.list_query_terms(coll)}')

    def list_collections(self) -> list:
        """
        Return a list of the names of collections for this Client
        """
        return [coll.id for coll in self._client.get_collections()]
    
    def display_collections(self):
        """
        Display the list of collections with their descriptions"""
        for coll in self._client.get_collections():
            print(f'{coll.id}: {coll.description}')

    def search(self, mappings: dict = None, **kwargs) -> DataPointSearch:
        """
        Perform a search operation, creates a ``DataPointSearch``
        object which is also self-describing."""

        mappings = mappings or self._mappings
        
        search = self._client.search(**kwargs)
        return DataPointSearch(search, search_terms=kwargs, meta=self._meta, parent_id=self._id, mappings=mappings)

