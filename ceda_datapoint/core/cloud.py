__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import json
import logging
import os

import fsspec
import requests
import rioxarray as rxr
import xarray as xr

from ceda_datapoint.mixins import PropertiesMixin, UIMixin
from ceda_datapoint.utils import hash_id, logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class DataPointMapper:
    """Mapper object for calling specific properties of an item"""
    def __init__(self, mappings: dict = None, id: str = None) -> None:
        self._mappings = mappings or {}
        self._id = id

    def set_id(self, id: str) -> None:
        """Set the ID for this mapper - cosmetic only"""
        self._id = id

    def get(self, key: str, stac_object: object) -> str:
        """
        Mapper.index('assets',stac_object)
        """

        def access(
                k: str, 
                stac_obj: object, 
                chain: bool = True
            ) -> str:
            """
            Error-accepting 'get' operation for an attribute from a STAC object - 
            with chain or otherwise."""
            try:
                if k in stac_obj:
                    return stac_obj[k]
                else:
                    return getattr(stac_obj, k)
            except (KeyError, ValueError, AttributeError):
                if chain:
                    logger.warning(
                        f'Chain for accessing attribute {key}:{self._mappings[key]} failed at {k}'
                    )
                else:
                    logger.warning(f'Property "{k}" for {self._id} is undefined.')
                return None

        if key in self._mappings:
            keychain = self._mappings[key].split('.')
            so = access(keychain[0], stac_object)
            for k in keychain[1:]:
                so = access(k, so)
                if so is None:
                    return None
        else:
            so = access(key, stac_object, chain=False)
        return so

class DataPointCloudProduct(PropertiesMixin):
    """
    Object for storing and manipulating a single cloud product
    i.e Kerchunk/Zarr/CFA.
    """

    def __init__(
            self,
            asset_stac: dict,
            id: str = None,
            cf: str = None,
            order: int = None,
            mode: str = 'xarray',
            meta: dict = None,
            stac_attrs: dict = None,
            properties: dict = None,
            mapper: DataPointMapper = None,
        ) -> None:

        """
        Initialise a single cloud product object. The cloud product has identical
        properties and attributes to the parent item, but now represents a single 
        reference dataset.
        
        :param asset_stac:  (dict) The asset as presented in the stac index.
        
        :param id:          (str) Identifier for this cloud product.
        
        :param cf:          (str) Cloud format type.
        
        :param order:       (int) Unused property relating to priority.
        
        :param mode:        (str) Method to use for opening dataset.
        
        :param meta:        (dict) DataPoint metadata relating to parent objects.
        
        :param stac_attrs:  (dict) Attributes of the item outside the ``properties``.
        
        :param properties:  (dict) Properties of the item in the ``properties`` field.
        """

        if mode != 'xarray':
            raise NotImplementedError(
                'Only "xarray" mode currently implemented - cf-python is a future option'
            )
        
        self._id = id
        self._order = order
        self._cloud_format = cf

        self._mapper = mapper or DataPointMapper(id)

        meta = meta or {}
        
        self._asset_stac = asset_stac
        self._meta = meta | {
            'asset_id': id,
            'cloud_format': cf
        }

        self._stac_attrs = stac_attrs
        self._properties = properties

        self.visibility = 'all'

        self._set_visibility()

    def __str__(self) -> str:
        return f'<DataPointCloudProduct: {self._id} (Format: {self._cloud_format})>'
    
    def __repr__(self) -> str:
        """Representation of this class using the meta components"""
        repr = super().__repr__().split('\n')
        repr.append('Attributes:')
        for k, v in self._properties.items():
            repr.append(f' - {k}: {v}')
        return '\n'.join(repr)
    
    @property
    def cloud_format(self) -> str:
        """Read-only property"""
        return self._cloud_format
    
    @property
    def href(self) -> str:
        """Read-only href property"""
        return self._mapper.get('href',self._asset_stac)

    def help(self) -> None:
        """Display public methods for this object."""
        print('DataPointCloudProduct Help:')
        print(' > product.info() - Get information about this cloud product.')
        print(' > product.open_dataset() - Open the dataset for this cloud product (in xarray)')
        super().help(additionals = ['href','cloud_format'])

    def info(self) -> None:
        """Display information about this object"""
        print(self.__repr__())

    def open_dataset(
            self, 
            local_only: bool = False, 
            **kwargs
        ) -> xr.Dataset:
        """
        Open the dataset for this product (in xarray).
        Specific methods to open cloud formats are private since
        the method should be determined by internal values not user
        input.

        :param local_only:  (bool) Switch to using local-only files - DataPoint will
            convert all hrefs and internal Kerchunk links to use local paths.
        """
        if not self._cloud_format:
            raise ValueError(
                'No cloud format given for this dataset'
            )
        
        if self.href is None:
            raise ValueError(
                'Cloud assets with no "href" are not supported'
            )
        
        if self.visibility == 'local-only' and not local_only:
            raise ValueError(
                'Href not reachable via https, please use `local_only=True` '
                'to open this dataset.'
            )

        try:
            if self._cloud_format == 'kerchunk':
                return self._open_kerchunk(local_only=local_only, **kwargs)
            elif self._cloud_format == 'CFA':
                return self._open_cfa(**kwargs)
            elif self._cloud_format == 'zarr':
                return self._open_zarr(**kwargs)
            elif self._cloud_format == 'cog':
                return self._open_cog(**kwargs)
            else:
                raise ValueError(
                    'Cloud format not recognised - must be one of ("kerchunk", "CFA", "zarr", "cog")'
                )
        except ValueError as err:
            raise err
        except FileNotFoundError:
            raise FileNotFoundError(
                'The requested resource could not be located: '
                f'{self.href}'
            )

    def _open_kerchunk(
            self,
            local_only: bool = False,
            **kwargs,
        ) -> xr.Dataset:
        
        """
        Open a kerchunk dataset in xarray
        
        :param local_only:  (bool) Switch to using local-only files - DataPoint will
            convert all hrefs and internal Kerchunk links to use local paths.
        """
                
        href = self.href
        mapper_kwargs = self._mapper.get('mapper_kwargs',self._asset_stac) or {}
        open_zarr_kwargs = self._mapper.get('open_zarr_kwargs', self._asset_stac) or {}

        if local_only:
            href = _fetch_kerchunk_make_local(href)

        mapper = fsspec.get_mapper(
            'reference://',
            fo=href,
            **mapper_kwargs
        )

        zarr_kwargs = _zarr_kwargs_default(add_kwargs=open_zarr_kwargs) | kwargs

        return xr.open_zarr(mapper, **zarr_kwargs)

    def _open_cfa(
            self,
            cfa_options: dict = None,
            **kwargs,
        ) -> xr.Dataset:

        """
        Open a CFA dataset in xarray
        
        :param cfa_options:     (dict) Configuration options to pass to the CFA engine
        """

        cfa_options = cfa_options or {}

        href = self.href

        open_xarray_kwargs = (self._mapper.get('open_xarray_kwargs', self._asset_stac) or {}) | kwargs

        return xr.open_dataset(
            href, 
            engine='CFA', cfa_options=cfa_options, **open_xarray_kwargs
        )

    def _open_zarr(
            self,
            **kwargs,
        ) -> xr.Dataset:

        open_zarr_kwargs = (self._mapper.get('open_zarr_kwargs', self._asset_stac) or {}) | kwargs

        return xr.open_dataset(self.href, engine='zarr', **open_zarr_kwargs)

    def _open_cog(
            self,
            **kwargs,
        ) -> xr.Dataset:

        open_cog_kwargs = (self._mapper.get('open_cog_kwargs', self._asset_stac) or {}) | kwargs

        return rxr.open_rasterio(self.href, **open_cog_kwargs)

    def _set_visibility(self) -> None:
        """Determine if this product is reachable"""
        if 'https://' in self.href:
            # Check remote link
            status = requests.head(self.href)
            if status.status_code != 200:
                self.visibility = 'local-only'
            else:
                return
        
        # Check local link
        local_ref = self.href.replace('https://dap.ceda.ac.uk','')
        if not os.path.isfile(local_ref):
            self.visibility = 'unreachable'

class DataPointCluster(UIMixin):
    """
    A set of non-combined datasets opened using the DataPointSearch
    ``to_dataset()`` method. Has some additional properties over a 
    list of datasets. """

    def __init__(
            self, 
            products: list, 
            parent_id: str = None, 
            meta: dict = None,
            local_only: bool = False,
            show_unreachable: bool = False
        ) -> None:
        
        """Initialise a cluster of datasets from a set of assets.
        
        :param products:    (list) A list of DataPoint cloud product objects.
         
        :param parent_id:   (str) ID of the parent search/item object.
         
        :param meta:        (dict) Metadata about the parent object.
        
        :param local_only:  (bool) Switch to using local-only files - DataPoint will
            convert all hrefs and internal Kerchunk links to use local paths.

        :param show_unreachable: (bool) Show the hidden assets that DataPoint has determined are currently unreachable.
        """
        
        self._id = f'{parent_id}-{hash_id(parent_id)}'

        self._local_only = local_only

        self.show_unreachable = show_unreachable

        meta = meta or {}

        self._products = {}

        for p in products:
            if isinstance(p, DataPointCluster):
                for sub_p in p.products:
                    self._products[sub_p.id] = sub_p
            elif p is not None:
                self._products[p.id] = p

        self._meta = meta
        self._meta['products'] = len(products)

    def __str__(self) -> str:
        """String representation of this class"""
        return f'<DataPointCluster: {self._id} (Datasets: {len(self._products)})>'
    
    def __getitem__(self, index):
        """
        Index this object to obtain a DataPointCloudProduct 
        by ID or position in the cluster.
        """

        if isinstance(index, int):
            index = list(self._products.keys())[index]

        if index not in self._products:
            raise IndexError(
                f'"{index}" not found in available products.'
            )
        return self._products[index]
    
    @property
    def products(self) -> list[DataPointCloudProduct]:
        """List of products contained within this cluster"""
        return [ v for v in self._products.values() if v.visibility != 'unreachable' or self.show_unreachable]

    def help(self) -> None:
        """Helper function - lists methods that can be utilised for this class"""
        print('DataPointCluster Help:')
        print(' > cluster.info() - basic cluster information')
        print(' > cluster.open_dataset(index/id) - open a specific dataset in xarray')
        super().help(additionals=['products'])

    def info(self) -> None:
        """Information about this object instance."""
        print(self.__repr__())

    def __repr__(self) -> str:
        """Notebooks representation of this class"""
        repr = super().__repr__().split('\n')
        repr.append('Products:')
        for p in self._products.values():
            if p.visibility != 'all':
                repr.append(f' - {p.id}: {p.cloud_format} ({p.visibility})')
            else:
                repr.append(f' - {p.id}: {p.cloud_format}')
        return '\n'.join(repr)
    
    def open_dataset(
            self,
            id : str,
            mode: str = 'xarray',
            local_only: bool = False,
            **kwargs,
        ) -> xr.Dataset:
        """
        Open a dataset from within this cluster's cloud products. A 
        dataset can be indexed either by id or position within this 
        cluster's set of datasets. 
        
        :param id:      (str) The ID or index of the dataset in the resulting cluster.
        
        :param mode:    (str) The type of dataset to be returned, currently only Xarray is supported (0.3.X)
        
        :param local_only:  (bool) Switch to using local-only files - DataPoint will
            convert all hrefs and internal Kerchunk links to use local paths."""
            
        if mode != 'xarray':
            raise NotImplementedError(
                'Only "xarray" mode currently implemented - cf-python is a future option'
            )
        
        local_only = local_only or self._local_only
        
        if isinstance(id, int):
            id = list(self._products.keys())[id]
        
        if id not in self._products:
            logger.warning(
                f'"{id}" not found in available datasets.'
            )
            return None
        
        product = self._products[id]
        return product.open_dataset(local_only=local_only, **kwargs)

    def open_datasets(self):
        raise NotImplementedError(
            '"Combine" feature has not yet been implemented'
        )

def _zarr_kwargs_default(add_kwargs: dict = None) -> dict:
    """Add any default kwargs for specific requests"""

    add_kwargs = add_kwargs or []

    defaults = {
        'consolidated':False,
    }
    return defaults | add_kwargs

def _fetch_kerchunk_make_local(href: str) -> dict:
    """
    Fetch a kerchunk file, open as json content and do find/replace
    to access local files only.
    """
    href_local = href.replace('https://dap.ceda.ac.uk','')
    if not os.path.isfile(href_local):
        attempts = 0
        success = False
        while attempts < 3 and not success:
            resp = requests.get(href)
            if resp.status_code == 200:
                success = True
            attempts += 1
        if attempts >= 3 and not success:
            raise ValueError(
                f'File {href}: Download unsuccessful - '
                'could not download the file successfully (tried 3 times)'
            )
        refs = json.loads(resp.text)
    else:
        with open(href_local) as f:
            refs = json.load(f)

    for key in refs['refs'].keys():
        v = refs['refs'][key]
        if isinstance(v, list) and len(v) == 3:
            # First character
            if 'https://' in v[0]:
                refs['refs'][key][0] = v[0].replace('https://dap.ceda.ac.uk/','/')
    return refs

