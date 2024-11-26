__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

class UIMixin:
    """
    Mixin for behaviours common to all User-facing classes.
    """

    @property
    def id(self):
        return self._id

    def help(self, additionals: list = None):
        """
        Link to documentation or other sources of assistance.
        """
        additionals = additionals or []

        properties = ['id', 'meta', 'collection'] + additionals
        print('Properties: ',', '.join(properties))
        print('See the documentation at https://cedadev.github.io/datapoint/')

    def __repr__(self):
        """Python representation of standard DataPoint metadata"""
        repr = [str(self)]
        for k, v in self._meta.items():
            repr.append(f' - {k}: {v}')
        return '\n'.join(repr)
    
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