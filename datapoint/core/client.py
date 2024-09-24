__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import pystac_client
from pystac_client.stac_api_io import StacApiIO

from datapoint.core.utils import urls
from datapoint.core.search import DataPointSearch

class DataPointClient:

    def __init__(self, org='CEDA', url=None):
        if not url:
            if org not in urls:
                raise ValueError(
                    f'Organisation "{org}" not recognised - please select from '
                    f'{list(urls.keys())}'
                )
            url = urls[org]

        self._url = url

        self._client = pystac_client.Client.open(url)

    def __str__(self):
        return 'Client for DataPoint searches.'

    def __repr__(self):
        return self.__str__()

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
        return DataPointSearch(search, search_terms=kwargs)