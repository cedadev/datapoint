__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

# DataPointStoreset class
#   methods: is_active, open_stores, close.

class DataPointStoreset:
    """
    The datapoint storeset is a wrapper to the stores for each individual cloud asset.
    Each cloud asset may have a different DataStore (CFADataStore, Kerchunk/Zarr etc.)
    This class seeks to open all given stores and combine the outputs *IF POSSIBLE*,
    but this is only the case if the coordinate variables do not interfere or can be 
    made to not interfere within a single xarray dataset. If this is not possible then
    the DataPointStoreset will not be used.
    """

    def __init__(self):
        pass

    def is_active(self):
        """
        Find out if any of the assets know about active storage.
        May also want this as a user-set parameter.
        """
        pass

    def open_stores(self):
        """
        Open the stores attributed to each asset and combine the vars,
        attrs, coordinates and encoding where possible.
        """
        pass

    def close(self):
        """
        Copy the close routines of each datastore here to then be passed
        to xarray directly.
        """
        pass