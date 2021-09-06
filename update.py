import urllib.request
import os

host = 'prd-priconne-redive.akamaized.net'
manifest_path = '/dl/Resources/%s/Jpn/AssetBundles/iOS/manifest/manifest_assetmanifest'
masterdata_path = '/dl/Resources/%s/Jpn/AssetBundles/Windows/manifest/masterdata_assetmanifest'
bundles_path = '/dl/pool/AssetBundles'
default_ver = 10031500
max_test_amount = 30
test_multiplier = 10

ver = default_ver
i = 0
while i < max_test_amount:
    guess = ver + i * test_multiplier
    url = f'http://{host}{manifest_path % guess}'
    try:
        response = urllib.request.urlopen(url)
        if response.code == 200:
            ver = guess
            i = 0
    except urllib.error.HTTPError:
        pass
    i += 1

urllib.request.urlretrieve(f'http://{host}{masterdata_path % ver}', 'masterdata')

cdb_path = 'master.cdb'
db_path = 'master.db'
with open('masterdata') as fd:
    hash_ = fd.readline().split(',')[1]
    urllib.request.urlretrieve(f'http://{host}{bundles_path}/{hash_[:2]}/{hash_}', cdb_path)

stream = os.popen(f'Coneshell_call.exe -cdb  {cdb_path} {db_path}')
output = stream.read()
print(output)

os.remove('masterdata')
os.remove('master.cdb')
