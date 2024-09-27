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