__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging

logger = logging.getLogger(__name__)

class PropertiesMixin:

    @property
    def id(self):
        """
        Attempt to get the stac id, or use the string
        representation of the source stac object."""

        return self._id
    
    @property
    def bbox(self):
        return self._stac_attrs['bbox']
    
    @property
    def start_datetime(self):
        return self._properties['start_datetime']
    
    @property
    def end_datetime(self):
        return self._properties['end_datetime']
         
    @property
    def attributes(self):
        """
        Attributes for this object listed under ``properties`` in the STAC record.
        """
        return self._properties
    
    @property
    def stac_attributes(self):
        """
        Top-level attributes for this object in the STAC record.
        """
        return self._stac_attrs

    @property
    def variables(self):
        """
        Return the ``variables`` for this object if present.
        """
        return self._multiple_options(['variables', 'variable_long_name'])

    @property
    def units(self):
        """
        Return the ``units`` for this object if present.
        """
        return self._multiple_options(['units', 'variable_units'])

    def _multiple_options(self, options):
        """
        Retrieve an attribute frokm the STAC record with multiple
        possible names. e.g units or Units.
        """
        attr = None
        for option in options:
            if option in self._properties:
                attr = self._properties[option]
                continue
            if hasattr(self._properties, option):
                attr = getattr(self._properties, option)
                continue

        if attr is None:
            logger.warning(
                f'Attribute not found from options: {options}'
            )

        return attr
    
    def get_attribute(self, attr):
        """
        Retrieve a specific attribute from this object's STAC Record,
        from either the ``stac attributes`` or properties.
        """

        if hasattr(self._properties, attr):
            return getattr(self._properties, attr)
        
        if attr in self._stac_attrs:
            return self._stac_attrs[attr]

        logger.warning(
            f'Attribute "{attr}" not found.'
        )
        return None
