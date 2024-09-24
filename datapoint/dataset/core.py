__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import fsspec
import xarray as xr

class DataPointCluster:
    """
    A set of non-combined datasets opened using the DataPointSearch
    ``to_dataset()`` method. Has some additional properties over a 
    list of datasets. """


    def __init__(self, dset, ids, **kwargs):

        self._dset = dset
        self._ids = ids

    def __str__(self):
        return f'<DataPointCluster: ({len(self._dset)})>'
    
    def __repr__(self):
        return '\n'.join([str(self)] + self.items())
    
    def __getitem__(self, index):
        if isinstance(index, str):
            index = self._ids.index(index)
        return self._dset[index] 
    
    def items(self):
        info = []
        for ds, id in zip(self._dset, self._ids):
            ds_ident = f'<DataPointProduct: {id}>'
            info.append(ds_ident)
        return info