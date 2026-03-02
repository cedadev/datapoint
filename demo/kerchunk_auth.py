import xarray as xr
import fsspec
import requests
import os, sys
import json
import ssl

import matplotlib.pyplot as plt

kfile = '/gws/ssde/j25b/eds_ai/high5/data/processing/padocc/in_progress/ukcp/land-cpm_uk_5km_rcp85_01_sfcWind_1hr/in_progress/ukcp1/ukcp_land-cpm_5km_rcp85_01_sfcWind_1hr/k1.0a.json'
CERT_FILE = "/home/users/dwest77/.globus/certificate-file"

use_token = ('--token' in sys.argv)

def get_auth():
    print('Getting Oauth Token')
    uname = ''
    pwd = ''
    csecret = ''
    cmd = f"""curl --location 'https://accounts.ceda.ac.uk/realms/ceda/protocol/openid-connect/token' --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'username={uname}' --data-urlencode 'password={pwd}' --data-urlencode 'client_id=bearer-token-test' --data-urlencode 'client_secret={csecret}' --data-urlencode 'grant_type=password' > jsons/token.json"""
    
    os.system(cmd)

    with open('jsons/token.json') as f:
        token = json.load(f)

    auth = {"Authorization":f"{token['token_type']} {token['access_token']}"}
    return None

def get_new_token(username, password):
    from base64 import b64encode

    url = "https://services.ceda.ac.uk/api/token/create/"

    #username = "dwest77"
    #password = "<PASSWORD>"
    token = b64encode(f"{username}:{password}".encode('utf-8')).decode("ascii")
    headers = {
        "Authorization": f'Basic {token}',
    }

    response = requests.request("POST", url, headers=headers)
    return {"Authorization": f"Bearer {json.loads(response.text)['access_token']}"}

def get_ssl_context():
    print('Setting up SSL context')
    # Set up ssl context
    ssl_context = ssl.create_default_context(cafile=CERT_FILE, capath=CERT_FILE)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context

def get_cookies():
    print('Getting Cookies')
    tiny_readme_url = "https://dap.ceda.ac.uk/badc/ukcp18/data/land-cpm/ancil/lsm/lsm_land-cpm_BI_5km.nc"
    r = requests.get(tiny_readme_url, cert=CERT_FILE, verify=False)
    print(r.content)
    return r.cookies

if use_token:
    print('Using New Schema Token')
    remote_options = {'headers':get_new_token(os.environ.get("CEDA_USERNAME"), os.environ.get("CEDA_PASSWORD"))}
else:
    print('Using SSL Certificate')
    remote_options = {'ssl':get_ssl_context(),'cookies':get_cookies()}

if __name__ == '__main__':

    print('Accessing Dataset', remote_options)
    ds = xr.open_dataset(kfile, engine='kerchunk', backend_kwargs={'storage_options':remote_options})
    print(ds)

#mapper = fsspec.get_mapper("reference://", fo=refs, remote_options=remote_options) 
#ds = xr.open_zarr(mapper, consolidated=False)