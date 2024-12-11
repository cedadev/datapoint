__author__    = "Daniel Westwood"
__contact__   = "daniel.westwood@stfc.ac.uk"
__copyright__ = "Copyright 2024 United Kingdom Research and Innovation"

import logging

logging.basicConfig(level=logging.WARNING)
logstream = logging.StreamHandler()

formatter = logging.Formatter('%(levelname)s [%(name)s]: %(message)s')
logstream.setFormatter(formatter)

# URLs for specific organisations stac catalogs
# NOTE: In future this may be extended to intake catalogs depending on demand and similarity.
urls = {
    'CEDA':'https://api.stac.ceda.ac.uk'
}

# Will at some point become deprecated but is currently needed for CMIP6/CCI records.
method_format = {
    'reference_file': 'kerchunk',
    'reference_file_2': 'CFA',
    'cog':'cog',
}

def generate_id():
    import random
    chars = [*'0123456789abcdefghijklmnopqrstuvwxyz']
    id = ''
    for i in range(6):
        j = random.randint(0,len(chars)-1)
        id += chars[j]

    return f'DP:{id}'

def hash_id(hash_token):
    hash_val=0
    for ch in hash_token:
        hash_val = ( hash_val*281  ^ ord(ch)*997) & 0xFFFFFFFF
    return str(hash_val)[:6]

def set_verbose(level: int):
    """
    Reset the logger basic config.
    """

    levels = [
        logging.WARN,
        logging.INFO,
        logging.DEBUG,
    ]

    if level >= len(levels):
        level = len(levels) - 1

    for name in logging.root.manager.loggerDict:
        lg = logging.getLogger(name)
        lg.setLevel(levels[level])
