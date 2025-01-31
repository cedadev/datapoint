__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging
from typing import Union

from ceda_datapoint.utils import logstream

from .general import UIMixin

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class PropertiesMixin(UIMixin):
    """
    Mixin for Item/Cloud product objects where specific properties
    apply to all sub-elements of the object.

    All Objects under PropertiesMixin must have a _mapper attachment.
    """
    __slots__ = ['_mapper']

    def help(self, additionals: list = None) -> None:
        """Get all properties of this Mixin"""

        additionals = additionals or []
        additionals += [
            'bbox', 'start_datetime', 
            'end_datetime', 'attributes',
            'stac_attributes','variables',
            'units'
        ]
        super().help(additionals=additionals)

    @property
    def bbox(self) -> list:
        """
        Get the bounding box for this object.
        Stac_attrs is mapper-aware."""
        return self._stac_attrs['bbox']
    
    @property
    def start_datetime(self) -> str:
        """Get the start datetime for this object.
        _properties is mapper-aware."""
        return self._properties['start_datetime']
    
    @property
    def end_datetime(self) -> str:
        """Get the end datetime for this object.
        _properties is mapper-aware."""
        return self._properties['end_datetime']
         
    @property
    def attributes(self) -> dict:
        """
        Attributes for this object listed under ``properties`` in the STAC record.
        _properties is mapper-aware.
        """
        return self._properties
    
    @property
    def stac_attributes(self) -> dict:
        """
        Top-level attributes for this object in the STAC record.
        _stac_attrs is mapper-aware.
        """
        return self._stac_attrs

    @property
    def variables(self) -> Union[str,list[str]]:
        """
        Return the ``variables`` for this object if present.
        """
        return self._multiple_options(['variables', 'variable_long_name'])

    @property
    def units(self) -> Union[str,list[str]]:
        """
        Return the ``units`` for this object if present.
        """
        return self._multiple_options(['units', 'variable_units'])

    def _multiple_options(self, options: list) -> Union[str,list[str]]:
        """
        Retrieve an attribute frokm the STAC record with multiple
        possible names. e.g units or Units.
        _properties is mapper-aware.
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
    
    def get_attribute(self, attr: str):
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
