__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import fsspec
import xarray as xr
import logging
import requests
import json

from ceda_datapoint.mixins import UIMixin, PropertiesMixin
from .utils import hash_id

logger = logging.getLogger(__name__)

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
            local_only: bool = False):
        
        self._id = f'{parent_id}-{hash_id(parent_id)}'

        self._local_only = local_only

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

    def __str__(self):
        return f'<DataPointCluster: {self._id} (Datasets: {len(self._products)})>'
    
    def __getitem__(self, index):

        if isinstance(index, int):
            index = list(self._products.keys())[index]

        if index not in self._products:
            logger.warning(
                f'"{index}" not found in available products.'
            )
            return None
        return self._products[index]
    
    @property
    def products(self):
        return list(self._products.values())

    def help(self):
        print('DataPointCluster Help:')
        print(' > cluster.info() - basic cluster information')
        print(' > cluster.display_datasets() - find information on datasets within this cluster')
        print(' > cluster.open_dataset(index/id) - open a specific dataset in xarray')
        super().help()

    def info(self):
        print(self)
        for p in self._products.keys():
            print(f' - {p}')

    def display_datasets(self):
        print(self)
        for p in self._products.values():
            print(f' - {p.id}: {p.cloud_format}')
    
    def open_dataset(
            self,
            id,
            mode: str = 'xarray',
            local_only: bool = False,
            **kwargs,
        ) -> xr.Dataset:
            
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

class DataPointCloudProduct(UIMixin, PropertiesMixin):

    def __init__(
            self,
            asset_dict: dict,
            id: str = None,
            cf: str = None,
            order: int = None,
            mode: str = 'xarray',
            meta: dict = None,
            stac_attrs: dict = None,
            properties: dict = None,
        ):

        if mode != 'xarray':
            raise NotImplementedError(
                'Only "xarray" mode currently implemented - cf-python is a future option'
            )
        
        self._id = id
        self._order = order
        self._cloud_format = cf
        
        self._asset_meta = asset_dict
        self._meta = meta | {
            'asset_id': id,
            'cloud_format': cf
        }

        self._stac_attrs = stac_attrs
        self._properties = properties

    @property
    def cloud_format(self):
        return self._cloud_format
    
    def __str__(self):
        return f'<DataPointCloudProduct: {self._id} (Format: {self._cloud_format})>'
    
    def help(self):
        print('DataPointCloudProduct Help:')
        print(' > product.info() - Get information about this cloud product.')
        print(' > product.open_dataset() - Open the dataset for this cloud product (in xarray)')
        super().help()

    def info(self):
        print(self)
        for k, v in self._meta.items():
            print(f' - {k}: {v}')

    def open_dataset(self, local_only: bool = False, **kwargs):
        """
        Open the dataset for this product (in xarray).
        Specific methods to open cloud formats are private since
        the method should be determined by internal values not user
        input.
        """
        if not self._cloud_format:
            raise ValueError(
                'No cloud format given for this dataset'
            )
        
        try:
            if self._cloud_format == 'kerchunk':
                return self._open_kerchunk(local_only=local_only, **kwargs)
            elif self._cloud_format == 'CFA':
                return self._open_cfa(**kwargs)
            else:
                raise ValueError(
                    'Cloud format not recognised - must be one of ("kerchunk", "CFA")'
                )
        except ValueError as err:
            raise err
        except FileNotFoundError:
            raise FileNotFoundError(
                'The requested resource could not be located: '
                f'{self._asset_meta["href"]}'
            )

    def _open_kerchunk(
            self,
            local_only: bool = False,
            **kwargs,
        ) -> xr.Dataset:
        
        """
        Open a kerchunk dataset in xarray"""
        
        if 'href' not in self._asset_meta:
            raise ValueError(
                'Cloud assets with no "href" are not supported'
            )
        href = self._asset_meta['href']
        
        mapper_kwargs = self._asset_meta.get('mapper_kwargs') or {}
        open_zarr_kwargs = self._asset_meta.get('open_zarr_kwargs') or {}

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
        Open a CFA dataset in xarray"""

        cfa_options = cfa_options or {}

        if 'href' not in self._asset_meta:
            raise ValueError(
                'Cloud assets with no "href" are not supported'
            )
        href = self._asset_meta['href']

        open_xarray_kwargs = (self._asset_meta.get('open_xarray_kwargs') or {}) | kwargs

        return xr.open_dataset(
            href, 
            engine='CFA', cfa_options=cfa_options, **open_xarray_kwargs
        )

def _zarr_kwargs_default(add_kwargs={}):

    defaults = {
        'consolidated':False,
    }
    return defaults | add_kwargs

def _fetch_kerchunk_make_local(href: str):
    """
    Fetch a kerchunk file, open as json content and do find/replace
    to access local files only.
    """
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

    for key in refs['refs'].keys():
        v = refs['refs'][key]
        if isinstance(v, list) and len(v) == 3:
            # First character
            if 'https://' in v[0]:
                refs['refs'][key][0] = v[0].replace('https://dap.ceda.ac.uk/','/')
    return refs

