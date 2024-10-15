__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

# URLs for specific organisations stac catalogs
# NOTE: In future this may be extended to intake catalogs depending on demand and similarity.
urls = {
    'CEDA':'https://api.stac.ceda.ac.uk'
}

# Will at some point become deprecated but is currently needed for CMIP6/CCI records.
method_format = {
    'reference_file': 'kerchunk',
    'reference_file_2': 'CFA',
}