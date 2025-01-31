__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

from xarray import conventions
from xarray.backends import BackendEntrypoint
from xarray.core.dataset import Dataset

# Installed DataPointGateway as an Xarray Engine under engine='DataPoint'
# - DataPointStoreset class
#   - methods: is_active, open_stores, close.

class DataPointGateway(BackendEntrypoint):

    description = "DataPoint-specific backend to enable to combine function"

    def open_dataset(
            self,
            datapoint_obj,
            *,
            drop_variables=None,
            mask_and_scale=None,
            decode_times=None,
            concat_characters=None,
            decode_coords=None,
            use_cftime=None,
            decode_timedelta=None,
            # backend specific keyword arguments
            # do not use 'chunks' or 'cache' here
        ):
        """
        Returns a complete xarray representation of a CFA-netCDF dataset which includes expanding/decoding
        CFA aggregated variables into proper arrays.
        """

        #assert isinstance(datapoint_obj, None)

        use_active = datapoint_obj.is_active()

        vars, attrs, encoding, coord_names = datapoint_obj.open_stores()

        # Create the xarray.Dataset object here.
        if use_active:
            try:
                from XarrayActive import ActiveDataset

                ds = ActiveDataset(vars, attrs=attrs)
            except ImportError:
                raise ImportError(
                    '"ActiveDataset" from XarrayActive failed to import - please '
                    'ensure you have the XarrayActive package installed.'
                )
        else:
            ds = Dataset(vars, attrs=attrs)
            
        ds = ds.set_coords(coord_names.intersection(vars))
        ds.set_close(datapoint_obj.close)
        ds.encoding = encoding

        return ds