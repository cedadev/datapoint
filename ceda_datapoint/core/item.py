__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging

from ceda_datapoint.mixins import PropertiesMixin, UIMixin
from .cloud import DataPointCloudProduct, DataPointCluster
from .utils import method_format

logger = logging.getLogger(__name__)

class DataPointItem(PropertiesMixin, UIMixin):
    """
    Class to represent a self-describing Item object from 
    the STAC collection."""

    def __init__(
            self, 
            item_stac: object, 
            meta: dict = None
        ):

        meta = meta or {}

        self._properties   = None
        self._assets       = None
        self._stac_attrs = {}

        self._id = 'N/A'
        if hasattr(item_stac,'id'):
            self._id = item_stac.id

        for key, value in item_stac.to_dict().items():
            if key == 'properties':
                self._properties = value
            elif key == 'assets':
                self._assets = value
            else:
                self._stac_attrs[key] = value

        self._collection = item_stac.get_collection().id

        self._meta = meta | {
            'collection': self._collection,
            'item': self._id,
            'assets': len(self._assets),
            'properties': len(self._properties.keys()),
            'stac_attrs': len(self._stac_attrs.keys()),
        }

        self._cloud_assets = self._identify_cloud_assets()

    def __str__(self):
        """
        String based representation of this instance.
        """
        return f'Collection: {self._collection}, Item: {self._id}'

    def __array__(self):
        """
        Return an array representation for this item, equating to the
        list of assets.
        """
        return list(self._assets.values())
    
    def __getitem__(self, index) -> dict:
        """
        Public method to index the dict of assets.
        """
        if isinstance(index, str):
            if index not in self._assets:
                logger.warning(
                    f'Asset "{index}" not present in the set of assets.'
                )
                return None
            return self._assets[index]
        elif isinstance(index, int):
            if index > len(self._assets.keys()):
                logger.warning(
                    f'Could not return asset "{index}" from the set '
                    f'of {len(self._assets)} assets.'
                )
                return None
            key = list(self._assets.keys())[index]
            return self._assets[key]
        else:
            logger.warning(
                f'Unrecognised index type for {index} - '
                f'must be one of ("int","str")'
            )
    
    def info(self):
        """
        Information about this item.
        """
        print(self.__str__())
        for k, v in self._meta:
            print(f' - {k}: {v}')

    def get_cloud_assets(
            self,
            priority=None,
        ) -> DataPointCluster:
        """
        Returns a cluster of DataPointCloudProduct objects representing the cloud assets
        as requested."""

        return self._load_cloud_assets(self, priority=priority)

    def get_assets(self) -> dict:
        """
        Get the set of assets (in dict form) for this item."""
        return self._assets

    def list_cloud_formats(self) -> list:
        """
        Return the list of cloud formats identified from the set
        of cloud assets."""

        return [i[1] for i in self._cloud_assets]

    def _identify_cloud_assets(
            self
        ) -> None:
        """
        Create the tuple set of asset names and cloud formats
        which acts as a set of pointers to the asset list, rather
        than duplicating assets.
        """

        rf_titles = list(method_format.keys())

        cloud_list = []
        for id, asset in self._assets.items():
            cf = None
            if 'cloud_format' in asset:
                cf = asset['cloud_format']
            elif id in rf_titles:
                cf = method_format[id]

            if cf is not None:
                cloud_list.append((id, cf))

        # Pointer to cloud assets in the main assets list.
        return cloud_list

    def _load_cloud_assets(
            self,
            priority: list = None,
        ) -> DataPointCluster:

        """
        Sets the cloud assets property with a cluster of DataPointCloudProducts or a 
        single DataPointCloudProduct if only one is present.
        """

        file_formats = list(method_format.values())

        priority = priority or file_formats

        asset_list = []
        for id, cf in self._cloud_assets:
            asset = self._assets[id]
            
            if cf in priority:
                # Register this asset as a DataPointCloudProduct
                order = priority.index(cf)
                asset_list.append(DataPointCloudProduct(asset, id=id, cf=cf, order=order, mode=mode))

        return DataPointCluster(asset_list, combine=combine, meta=self._meta)
    