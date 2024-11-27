__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging
import xarray

from ceda_datapoint.mixins import PropertiesMixin, UIMixin
from ceda_datapoint.utils import method_format, logstream

from .cloud import DataPointCloudProduct, DataPointCluster

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class DataPointItem(PropertiesMixin):
    """
    Class to represent a self-describing Item object from 
    the STAC collection."""

    def __init__(
            self, 
            item_stac: object, 
            meta: dict = None
        ):
        """
        DataPointItem initialisation, requires the original STAC record
        plus the meta information about parent objects within DataPoint.
        
        :param item_stac:   (object) A pystac Item object (to be abstracted)

        :param meta:        (dict) Metadata about the parent object.
        """

        self._meta = {}

        if item_stac is None:
            raise ValueError(
                'DataPointItem could not be initialised from empty STAC Item'
            )

        self._item_stac = item_stac

        self._id = 'N/A'
        if hasattr(item_stac,'id'):
            self._id = item_stac.id

        # Identify - does not create duplicates.
        self._cloud_assets = self._identify_cloud_assets()

        self._meta = meta | {
            'collection': self._collection,
            'item': self._id,
            'assets': len(self._assets),
            'cloud_assets': len(self._cloud_assets),
        }
        if self._properties:
            self._meta['attributes'] = len(self._properties.keys())
        if self._stac_attrs:
            self._meta['stac_attributes'] = len(self._stac_attrs.keys())


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
    
    def __repr__(self):
        """
        Representation of this item - includes
        meta and properties information
        """
        repr = super().__repr__().split('\n')
        repr.append('Properties:')
        for k, v in self._properties.items():
            repr.append(f' - {k}: {v}')
        return '\n'.join(repr)

    def __dict__(self):
        """Returns the original stac item record in JSON format."""
        return self._item_stac.to_dict()

    @property
    def _properties(self):
        """Fetch properties from item_stac"""
        try:
            properties = self._item_stac.to_dict()['properties'] or []
        except KeyError:
            logger.warning(f'Unable to read `properties` attribute from item {self._id}')
            properties = []
        return properties
    
    @property
    def _assets(self):
        """Fetch assets from item_stac"""
        try:
            assets = self._item_stac.to_dict()['assets'] or []
        except KeyError:
            logger.warning(f'Unable to read `assets` attribute from item {self._id}')
            assets = []
        return assets
    
    @property
    def _stac_attrs(self):
        """Fetch ``stac_attrs`` from item_stac"""
        attrs = {}
        for k, v in self._item_stac.to_dict().items():
            if k not in ['properties','assets']:
                attrs[k] = v
        return attrs
    
    @property
    def _collection(self):
        """Fetch collection id from item_stac"""
        return self._item_stac.get_collection().id
    
    @property
    def cloud_assets(self):
        """Lazily identify cloud assets"""
        return [self._assets[i[0]] for i in self._cloud_assets]

    def help(self):
        """Help method for this class"""
        print('DataPointItem Help:')
        print(' > item.info() - Get information about this item')
        print(' > item.get_cloud_product() - Get a particular cloud product by index')
        print(' > item.collect_cloud_assets() - Collect cloud products into a cluster')
        print(' > item.open_dataset() - Open a specific dataset (default 0) attributed to this item')
        print(' > item.list_cloud_formats() - Get a list of the cloud formats available for this item.')
        print(' > item.display_cloud_formats() - Display the list of cloud formats available.')
        super().help(additionals = ['cloud_assets'])

    def info(self):
        """
        Information about this item.
        """
        print(self.__repr__())

    def get_cloud_product(
            self, 
            id: int = 0,
            priority: list = None
        ) -> DataPointCloudProduct:
        """
        Returns a cloud product represented by this item from its cluster.
        The nth cloud product is returned given the ``id`` parameter. 
        Typically items should have only 1-2 cloud products attached.

        :param id:      (str) The ID or index of the dataset in the resulting cluster.
        
        :param priority: (list) Order by which to open a set of datasets.
        """

        product = self._load_cloud_assets(priority=priority)

        if isinstance(product, DataPointCloudProduct):
            if isinstance(id, int) and id != 0:
                raise IndexError(
                    f'Item contains only one cloud product - cannot access {id}'
                )
            elif isinstance(id, str):
                if product.id != id:
                    raise ValueError(
                        f'Requested ID ({id}) not found - available: ({product.id})'
                    )
            return product
        elif isinstance(product, DataPointCluster):
            return product[id]
        else:
            logger.warning(
                'Item failed to retrieve a dataset'
            )
            return None
        
    def open_dataset(
            self, 
            id: int = 0,
            priority: list = None,
            **kwargs
        ) -> xarray.Dataset:
        """
        Open a specific dataset, skip retrieving the cloud product
        
        :param id:      (str) The ID or index of the dataset.
        
        :param priority: (list) Order by which to open a set of datasets.
        """
        prod = self.get_cloud_product(id=id, priority=priority)
        return prod.open_dataset(**kwargs)

    def collect_cloud_assets(
            self,
            priority: list = None,
            show_unreachable: bool = False,
        ) -> DataPointCluster:
        """
        Returns a cluster of DataPointCloudProduct objects representing the cloud assets
        as requested.
        
        :param priority: (list) Order by which to open a set of datasets.

        :param show_unreachable: (bool) Show the hidden assets that DataPoint has determined are currently unreachable.
        """

        return self._load_cloud_assets(priority=priority, show_unreachable=show_unreachable)

    def get_assets(self) -> dict:
        """
        Get the set of assets (in dict form) for this item."""
        return self._assets

    def list_cloud_formats(self) -> list:
        """
        Return the list of cloud formats identified from the set
        of cloud assets."""

        return [i[1] for i in self._cloud_assets]
    
    def display_cloud_formats(self):
        """
        Display the list of cloud formats based on the cloud assets."""
        for i in self.cloud_assets:
            print(f'{i[0]}: {i[1]}')

    def _identify_cloud_assets(self) -> None:
        """
        Create the tuple set of asset names and cloud formats
        which acts as a set of pointers to the asset list, rather
        than duplicating assets.
        """
        assets = self._assets or []

        cloud_list = []
        if len(assets) == 0:
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
            show_unreachable: bool = False
        ) -> DataPointCluster:

        """
        Sets the cloud assets property with a cluster of DataPointCloudProducts or a 
        single DataPointCloudProduct if only one is present.
        
        :param priority: (list) Order by which to open a set of datasets.

        :param show_unreachable: (bool) Show the hidden assets that DataPoint has determined are currently unreachable.
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
                if show_unreachable or a.visibility != 'unreachable':
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
    