__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

class UIMixin:
    """
    Mixin for behaviours common to all User-facing classes.
    """

    def help(self):
        """
        Link to documentation or other sources of assistance.
        """
        print('See the documentation at https://cedadev.github.io/datapoint/')

    def __repr__(self):
        return str(self)
    
    def __dict__(self):
        """
        Dictionary Representation for User-facing classes."""
        return self._meta

    @property
    def meta(self):
        """
        Retrieve the ``meta`` values (read-only)
        """
        return self._meta
    
    @property
    def collection(self):
        """Retrieve the collection name (read-only)"""
        return self._collection