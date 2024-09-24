__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

from datapoint.dataset import open_kerchunk

from .properties import ItemPropertiesMixin

class DataPointItem(ItemPropertiesMixin):

    def __init__(self, item_stac):
        self._stac = item_stac.to_dict()

        self._cloud_assets = None
        self._collection = item_stac.get_collection().id

    def __str__(self):
        """
        String based representation of this instance.
        """
        return f'<Item: {self.id}>'

    def __repr__(self):
        """
        Programmer representation, identical to string representation
        for this class."""
        return self.__str__()
        
    @property
    def collection(self):
        return self._collection

    def cloud_assets(self):
        if self._cloud_assets is None:
            self._get_cloud_assets()
        return self._cloud_assets

    def _get_cloud_assets(self):
        known_assets = ['reference_file']

        assets = []
        asset_dict = self._stac.get_assets()
        for asset in asset_dict.keys():
            if asset in known_assets:
                assets.append(asset)
        self._cloud_assets = assets

    def open_dataset(
            self,
            mode='xarray',
            combine=False,
            priority=[],
        ):

        if mode != 'xarray':
            raise NotImplementedError
        
        if combine:
            raise NotImplementedError
        
        assets = self._stac.get_assets()

        if 'reference_file' in assets.keys():
            rf = assets['reference_file']

            return open_kerchunk(**rf.to_dict())