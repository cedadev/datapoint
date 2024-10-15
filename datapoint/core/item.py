__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

from datapoint.mixins.properties import ItemPropertiesMixin

from .cloud import DataPointCloudProduct, DataPointCluster

from .utils import method_format

class DataPointItem(ItemPropertiesMixin):

    def __init__(self, item_stac):

        self._properties   = None
        self._cloud_assets = None
        self._assets       = None
        self._attrs = {}

        for key, value in item_stac.to_dict().items():
            if key == 'properties':
                self._properties = value
            elif key == 'assets':
                self._assets = value
            else:
                self._attrs[key] = value

        self._collection = item_stac.get_collection().id

    def __str__(self):
        """
        String based representation of this instance.
        """
        return f'<Item: {self.id}>'

    def __repr__(self):
        """
        Programmer representation, identical to string representation
        for this class."""
        return self.__str__()
    
    def __dict__(self):
        return self.get_attributes()
        
    @property
    def collection(self):
        return self._collection

    def get_cloud_assets(
            self,
            mode='xarray',
            combine=False,
            priority=None,
            **kwargs,
        ):
        """
        Returns a cluster of DataPointCloudProduct objects representing the cloud assets
        as requested."""

        if mode != 'xarray':
            raise NotImplementedError(
                'Only "xarray" mode currently implemented - cf-python is a future option'
            )
        
        if combine:
            raise NotImplementedError(
                '"Combine" feature has not yet been implemented'
            )

        if self._cloud_assets is None:
            self._load_cloud_assets(self, mode=mode, combine=combine, priority=priority)

        return self._cloud_assets

    def _load_cloud_assets(
            self,
            mode='xarray',
            combine=False,
            priority=None,
            **kwargs,
        ):

        """
        Sets the cloud assets property with a cluster of DataPointCloudProducts or a 
        single DataPointCloudProduct if only one is present."""

        # priority: kerchunk, CFA etc.

        # Determine the assets within this item that match 'reference_file'
        # For each asset
        # If the asset has a 'cloud_format' attribute, check it against priority
          # If priority is None we don't need to check
          # Otherwise if the format is not in the priority we can ignore it.
          # At this stage open both priority things to pass to a cluster later.
        # No cloud format, match the asset name to `method format` in utils.

        rf_titles = list(method_format.keys())
        file_formats = list(method_format.values())

        priority = priority or file_formats

        asset_list = []
        for id, asset in self._assets.items():
            ignore = False
            if 'cloud_format' in asset:

                cf = asset['cloud_format']
                if cf not in priority:
                    ignore = True

            else:
                if id in rf_titles:
                    cf = method_format[id]
                    if cf not in priority:
                        ignore = True

            if not ignore:
                # Register this asset as a DataPointCloudProduct
                order = priority.index(cf)
                asset_list.append(DataPointCloudProduct(asset, order=order, mode=mode))

        return DataPointCluster(asset_list, combine=combine)

        funcs = {}

        reached_file = False
        count = 1
        while not reached_file and count < 10:
            ref_file = 'reference_file'
            if count > 2:
                ref_file += f'_{count}'

            if ref_file in assets:
                asset = assets[ref_file]

                if 'cloud_format' in asset:
                    if asset['cloud_format'] in known_formats:
                        funcs[asset['cloud_format']] = (known_formats[asset['cloud_format']], ref_file)
                    else:
                        print('Unrecognised cloud format')
                else:
                    print('No cloud format detected')
                    if ref_file in known_methods:
                        funcs[method_format[ref_file]] = (known_methods[ref_file], ref_file)
                    else:
                        print('Unknown reference file type')
            count += 1

        for cloud_type in priority:
            if cloud_type in funcs:

                try:
                    (func, rf) = funcs[cloud_type]
                    rf   = assets[rf] | kwargs
                    return func(**rf)
                except KeyError:
                    # Future raise warning
                    continue

        raise ValueError(
            'Priority list does not include a valid cloud format'
            f'Available format options: {tuple(known_methods.keys())}'
        )
    