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

        assets, properties = None, None

        for key, value in item_stac.to_dict().items():
            if key == 'properties':
                properties = value
            elif key == 'assets':
                assets = value
            else:
                self._stac_attrs[key] = value

        self._assets = assets or {}
        self._properties = properties or {}

        self._collection = item_stac.get_collection().id

        self._cloud_assets = self._identify_cloud_assets()

        self._meta = meta | {
            'collection': self._collection,
            'item': self._id,
            'assets': len(self._assets),
            'cloud_assets': len(self._cloud_assets),
            'attributes': len(self._properties.keys()),
            'stac_attributes': len(self._stac_attrs.keys()),
        }

    def __str__(self):
        """
        String based representation of this instance.
        """
        return f'<DataPointItem: {self._id} (Collection: {self._collection})>'

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
    
    def help(self):
        print('DataPointItem Help:')
        print(' > item.info() - Get information about this item')
        print(
            ' > item.get_cloud_assets() - Recommended way of accessing '
            'all cloud datasets via a DataPointCluster')
        print(' > item.open_dataset() - Open a specific dataset (default 0) attributed to this item')
        print(' > item.list_cloud_formats() - List the cloud formats available for this item.')
        super().help()

    def info(self):
        """
        Information about this item.
        """
        print(self)
        for k, v in self._meta.items():
            print(f' - {k}: {v}')

    def open_dataset(
            self, 
            id: int = 0,
            priority: list = None,
            **kwargs
        ):
        """
        Returns a dataset represented by this item from its cluster.
        The nth dataset is returned given the ``id`` parameter. Typically
        items should have only 1-2 datasets attached.
        """

        cluster = self._load_cloud_assets(priority=priority)

        if isinstance(cluster, DataPointCloudProduct):
            return cluster.open_dataset(**kwargs)
        elif isinstance(cluster, DataPointCluster):
            return cluster[id].open_dataset(**kwargs)
        else:
            logger.warning(
                'Item failed to retrieve a dataset'
            )
            return None

    def get_cloud_assets(
            self,
            priority=None,
        ) -> DataPointCluster:
        """
        Returns a cluster of DataPointCloudProduct objects representing the cloud assets
        as requested."""

        return self._load_cloud_assets(priority=priority)

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
        cloud_list = []
        if self._assets is None:
            return cloud_list

        rf_titles = list(method_format.keys())

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
                asset_id = f'{self._id}-{id}'
                a = DataPointCloudProduct(
                    asset, 
                    id=asset_id, cf=cf, order=order, meta=self._meta,
                    stac_attrs=self._stac_attrs, properties=self._properties)
                asset_list.append(a)

        if len(asset_list) == 0:
            logger.warning(
                f'No dataset from {priority} found (id={self._id})'
            )
            return None
        elif len(asset_list) > 1:
            return DataPointCluster(asset_list, meta=self._meta, parent_id=self._id)
        else:
            return asset_list[0]
    