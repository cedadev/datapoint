__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

class ItemPropertiesMixin:

    @property
    def id(self):
        """
        Attempt to get the stac id, or use the string
        representation of the source stac object."""

        return self._multiple_options(['id', 'instance_id'])
    
    @property
    def assets(self):
        return list(self._stac['assets'].keys())

    @property
    def bbox(self):
        return self._stac['bbox']
    
    @property
    def start_datetime(self):
        return self._stac['start_datetime']
    
    @property
    def end_datetime(self):
        return self._stac['end_datetime']
    
    def _multiple_options(self, options):
        for option in options:
            if hasattr(self._stac, option):
                attr = getattr(self._stac, option)
                continue

        if not isinstance(attr, list):
            attr = [attr]
        return attr
    
    @property
    def variables(self):
        return self._multiple_options(['variables', 'variable_long_name'])

    @property
    def units(self):
        return self._multiple_options(['units', 'variable_units'])

    def get_attribute(self, attr):
        if hasattr(self._stac, attr):
            return getattr(self._stac, attr)
        
        raise ValueError(
            f'"{attr}" not found in item properties.'
        )
    
    def get_attributes(self):
        return self._stac
