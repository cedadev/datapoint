__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import xarray as xr
import fsspec

def zarr_kwargs_default(add_kwargs={}):

    defaults = {
        'consolidated':False,
    }
    return defaults | add_kwargs

def open_kerchunk(
        href,
        mapper_kwargs={},
        open_zarr_kwargs={},
        **kwargs
        ):
    
    mapper = fsspec.get_mapper(
        'reference://',
        fo=href,
        **mapper_kwargs
    )

    zarr_kwargs = zarr_kwargs_default(add_kwargs=open_zarr_kwargs)

    return xr.open_zarr(mapper, **zarr_kwargs)