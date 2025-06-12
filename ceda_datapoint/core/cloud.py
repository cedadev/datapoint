__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import json
import logging
import os
from typing import Any, Union

import fsspec
import requests
import rioxarray as rxr
import xarray as xr

from ceda_datapoint.core.asset import BasicAsset, DataPointMapper
from ceda_datapoint.mixins import PropertiesMixin, UIMixin
from ceda_datapoint.utils import hash_id, logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

def _decode_polygon(spatial_dims: list, coordinates: list) -> dict:
    """
    Decode GeoJSON Polygon to Xarray Selection.
    """
    selects = {}
    for i, dim in enumerate(spatial_dims):
        corners = [c[i] for c in coordinates]
        dim_range = slice(min(corners),max(corners))
        selects[dim] = dim_range
    return selects

def _decode_datetime(datetime):
    """
    Decode pystac datetime to xarray select.
    """
    dt = datetime.split('/')
    if len(dt) > 1:
        return slice(dt[0],dt[1])
    elif len(dt) == 1:
        return dt[0]
    else:
        return dt

def _find_spatial_dims(ds) -> Union[list,None]:
    """
    Determine the names of the spatial dims.
    """

    accepted_lats = ['lat','latitude','Lat','Latitude']
    accepted_lons = ['lon','longitude','Lon','Longitude']

    convention = None

    for convent in range(len(accepted_lats)):
        lat = accepted_lats[convent]
        lon = accepted_lons[convent]
        if lat in ds.dims and lon in ds.dims:
            convention = convent

    if convention is None:
        logger.warning(
            'Spatial AOI Skipped - Could not identify spatial dims. '
            f'Accepted dimensions are {accepted_lats} and {accepted_lons}'
        )
        return None
    
    lat = accepted_lats[convention]
    lon = accepted_lons[convention]

    # Determine lat/lon ordering in dataset.
    lat_ind = list(ds.dims).index(lat)
    lon_ind = list(ds.dims).index(lon)
    if lat_ind > lon_ind:
        return [lon, lat]
    else:
        return [lat, lon]

class DataPointCloudProduct(BasicAsset):
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
            data_selection: dict = None,
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
        
        super().__init__(
            asset_stac,
            id=id, meta=meta,
            stac_attrs=stac_attrs,
            properties=properties,
            mapper=mapper,
        )
        
        self._order = order
        self._cloud_format = cf

        self._data_selection = data_selection or {}

        self._meta['cloud_format'] = cf

        self.visibility = 'all'

        self._set_visibility()

    def __str__(self) -> str:
        return f'<DataPointCloudProduct: {self._id} (Format: {self._cloud_format})>'
    
    def __repr__(self) -> str:
        """Representation of this class using the meta components"""
        repr = super().__repr__().split('\n')
        repr.append('Attributes:')
        if self._properties is None:
            repr.append('   <empty>')
            return '\n'.join(repr)
        
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

    def open_asset(
            self,
            local_only: bool = False,
            prepare_data: bool = True,
            **kwargs
        ) -> Any:
        """
        Override for basic asset get function.
        """
        return self.open_dataset(local_only=local_only, prepare_data=prepare_data)

    def open_dataset(
            self, 
            local_only: bool = False,
            prepare_data: bool = True,
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
                ds = self._open_kerchunk(local_only=local_only, **kwargs)
            elif self._cloud_format == 'CFA':
                ds = self._open_cfa(**kwargs)
            elif self._cloud_format == 'zarr':
                ds = self._open_zarr(**kwargs)
            elif self._cloud_format == 'cog':
                ds = self._open_cog(**kwargs)
            else:
                raise ValueError(
                    'Cloud format not recognised - must be one of ("kerchunk", "CFA", "zarr", "cog")'
                )
            
            return self._prepare_dataset(ds, prepare_data=prepare_data)

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
            mapper_kwargs: dict = None,
            **kwargs,
        ) -> xr.Dataset:
        
        """
        Open a kerchunk dataset in xarray
        
        :param local_only:  (bool) Switch to using local-only files - DataPoint will
            convert all hrefs and internal Kerchunk links to use local paths.

        :param mapper_kwargs: (dict) Kwargs to provide to Kerchunk's fsspec mapper.
        """

        mapper_kwargs = mapper_kwargs or {}
                
        href = self.href
        mapper_kwargs = self._mapper.get('mapper_kwargs',self._asset_stac) or mapper_kwargs
        open_zarr_kwargs = self._mapper.get('open_zarr_kwargs', self._asset_stac) or {}

        if local_only:
            href = _fetch_kerchunk_make_local(href)

        return xr.open_dataset(href, engine='kerchunk',**open_zarr_kwargs)

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

    def _prepare_dataset(
            self, 
            ds: xr.Dataset, 
            prepare_data: bool = True
        ) -> Union[xr.Dataset, xr.DataArray]:
        """Perform any dataset selections here."""

        intersects = self._meta['search_terms'].get('intersects',None)
        # Intersection applies to spatial data

        datetime = self._meta['search_terms'].get('datetime',None)
        # Datetime can only be applied to 'time' dimension.

        query = self._meta['search_terms'].get('query',{})
        vq = query.get('variables',None)

        variables = self._data_selection.get('variables',None) or vq
        sel = self._data_selection.get('sel',None)
        isel = self._data_selection.get('isel',None)

        spatial_dims = None
        if intersects:
            # Order spatial dims correctly based on bbox
            spatial_dims = _find_spatial_dims(ds)

        if spatial_dims is not None:
            if intersects['type'] == 'Polygon':

                if len(intersects['coordinates']) == 1:
                    coords = intersects['coordinates'][0]
                else:
                    coords = intersects['coordinates']

                select = _decode_polygon(spatial_dims, coords)
                ds = ds.sel(**select)
            else:
                logger.warning(
                    'Unsupported intersection type for Single Search Selection - ' \
                    'AOI not applied.'
                )

        if datetime is not None:
            if 'time' not in ds:
                logger.warning(
                    'Datetime selection could not be applied - ',
                    'no "time" dimension present.'
                )
            else:
                if isinstance(datetime, str):
                    time_sel = _decode_datetime(datetime)
                else:
                    time_sel = slice(datetime[0],datetime[1])
                ds = ds.sel(time=time_sel)

        if variables is not None:

            if isinstance(variables,str):
                variables = [variables]

            keep_vars = []
            all_vars = list(ds.variables)
            for v in variables:
                if v not in ds:
                    logger.warning(
                        'Variable selection could not be applied - ',
                        f'no "{v}" variable present.'
                    )
                else:
                    keep_vars.append(v)
            if len(keep_vars) == 0:
                raise ValueError(
                    f'No variables kept in current selection - {variables}'
                )
            
            drop_vars = list(set(all_vars).difference(set(keep_vars)))
            ds = ds.drop_vars(drop_vars)

        if sel is not None:
            ds = ds.sel(**sel)
        if isel is not None:
            ds = ds.isel(**isel)

        return ds
                

    def _set_visibility(self) -> None:
        """Determine if this product is reachable"""

        if self.href.startswith('/'):
            # Check local path
            self.visibility = 'local-only'
            if not os.path.isfile(self.href):
                self.visibility = 'unreachable'
            return

        # Check remote link
        check_ref = self.href
        if self._cloud_format == 'zarr':
            check_ref = f'{self.href}/.zmetadata'

        status = requests.head(check_ref)
        if status.status_code != 200:
            # Check local link
            self.visibility='local-only'
            local_ref = self.href.replace('https://dap.ceda.ac.uk','')
            if not os.path.isfile(local_ref):
                self.visibility = 'unreachable'
            return
        return

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
            data_selection: Union[dict,None] = None,
            show_unreachable: bool = False,
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
        self._data_selection = data_selection

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

    add_kwargs = add_kwargs or {}

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

