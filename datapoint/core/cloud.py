__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import fsspec
import xarray as xr

from datapoint.mixins import DataPointMixin

class DataPointCluster(DataPointMixin):
    """
    A set of non-combined datasets opened using the DataPointSearch
    ``to_dataset()`` method. Has some additional properties over a 
    list of datasets. """


    def __init__(self, products, meta=None, combine=False, **kwargs):

        if combine:
            raise NotImplementedError(
                '"Combine" feature has not yet been implemented'
            )

        self._meta = meta
        self._combine = combine

        self._products = {str(p): p for p in products}

    def __str__(self):
        return f'<DataPointCluster: ({len(self._products.keys())})>'
    
    def __repr__(self):
        return self.__str__()
    
    def __getitem__(self, index):
        if index in self._products:
            return self._products[index]
        return None
    
    def open_datasets(self):
        pass

class DataPointCloudProduct:
    pass

def zarr_kwargs_default(add_kwargs={}):

    defaults = {
        'consolidated':False,
    }
    return defaults | add_kwargs

def open_kerchunk(
        href,
        mapper_kwargs=None,
        open_zarr_kwargs=None,
        decode_times=False,
        **kwargs,
        ):

    mapper_kwargs    = mapper_kwargs or {}
    open_zarr_kwargs = open_zarr_kwargs or {}
    
    mapper = fsspec.get_mapper(
        'reference://',
        fo=href,
        **mapper_kwargs
    )

    zarr_kwargs = zarr_kwargs_default(add_kwargs=open_zarr_kwargs)

    return xr.open_zarr(mapper, **zarr_kwargs)

def open_cfa(
    href,
    cfa_options=None,
    decode_times=None,
    **kwargs,
    ):

    cfa_options = cfa_options or {}

    return xr.open_dataset(
        href, 
        engine='CFA', cfa_options=cfa_options, decode_times=decode_times
    )
