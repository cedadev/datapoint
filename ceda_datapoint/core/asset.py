import logging
from typing import Any, Union

from ceda_datapoint.mixins import PropertiesMixin
from ceda_datapoint.utils import logstream

logger = logging.getLogger(__name__)
logger.addHandler(logstream)
logger.propagate = False

class DataPointMapper:
    """Mapper object for calling specific properties of an item"""
    def __init__(self, mappings: dict = None, id: str = None) -> None:
        self._mappings = mappings or {}
        self._id = id

    def set_id(self, id: str) -> None:
        """Set the ID for this mapper - cosmetic only"""
        self._id = id

    def get(self, key: str, stac_object: object) -> str:
        """
        Mapper.index('assets',stac_object)
        """

        def access(
                k: str, 
                stac_obj: object, 
                chain: bool = True
            ) -> str:
            """
            Error-accepting 'get' operation for an attribute from a STAC object - 
            with chain or otherwise."""
            try:
                if hasattr(stac_obj,k):
                    return getattr(stac_obj, k)
                else:
                    return stac_obj[k]
            except (KeyError, ValueError, AttributeError, TypeError):
                if chain:
                    logger.debug(
                        f'Chain for accessing attribute {key}:{self._mappings[key]} failed at {k}'
                    )
                else:
                    logger.debug(f'Property "{k}" for {self._id} is undefined.')
                return None

        if key in self._mappings:
            keychain = self._mappings[key].split('.')
            so = access(keychain[0], stac_object)
            for k in keychain[1:]:
                so = access(k, so)
                if so is None:
                    return None
        else:
            so = access(key, stac_object, chain=False)
        return so

class BasicAsset(PropertiesMixin):
    """
    Basic wrapper class for Any asset."""

    def __init__(
        self,
        asset_stac: dict,
        id: str = None,
        meta: dict = None,
        stac_attrs: dict = None,
        properties: dict = None,
        mapper: DataPointMapper = None,
    ) -> None:
        
        """
        Initialise a single contained asset. The asset has identical
        properties and attributes to the parent item, but now represents a single 
        asset.
        
        :param asset_stac:  (dict) The asset as presented in the stac index.
        
        :param id:          (str) Identifier for this cloud product.
        
        :param meta:        (dict) DataPoint metadata relating to parent objects.
        
        :param stac_attrs:  (dict) Attributes of the item outside the ``properties``.
        
        :param properties:  (dict) Properties of the item in the ``properties`` field.
        """
        
        self._id = id

        self._mapper = mapper or DataPointMapper(id)

        meta = meta or {}

        self._asset_stac = asset_stac
        self._meta = meta | {
            'asset_id': id,
        }
        
        self._asset_type = asset_stac.get('type',None)

        self._stac_attrs = stac_attrs
        self._properties = properties

    def __str__(self):
        """String representation of the asset"""
        return f'<DataPointAsset: {self._id}>'

    def open_asset(
            self,
            **kwargs
        ) -> Any:
        """
        Open different asset files with the correct implementation
        """

        raise NotImplementedError(
            'This feature is not yet implemented for datapoint v1.0'
        )

        if self._asset_type == 'application/netcdf':
            return None
            # Open as netcdf - h5netcdf for cloud?
            # Skipped feature for v1.0

        