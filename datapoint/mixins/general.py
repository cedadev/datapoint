__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

class DataPointMixin:

    def help():
        print('Link to documentation')

    def __repr__(self):
        return self._meta

    @property
    def meta(self):
        return self._meta