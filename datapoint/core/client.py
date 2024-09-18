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
        pass

    def __repr__(self):
        pass

    def __getitem__(self, collection):
        """
        Routine for getting a collection from this client
        """
        return DataPointSearch(self.search(collections=[collection]))
    
    @property
    def description(self):
        pass

    @property
    def id(self):
        pass

    @property
    def title(self):
        pass

    def links(self):
        pass

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
        return DataPointSearch(search, **kwargs)