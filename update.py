import json
import os
from shutil import copy
import sqlite3
import urllib.request

host = "prd-priconne-redive.akamaized.net"
manifest_path = "/dl/Resources/%s/Jpn/AssetBundles/iOS/manifest/manifest_assetmanifest"
masterdata_path = (
    "/dl/Resources/%s/Jpn/AssetBundles/Windows/manifest/masterdata_assetmanifest"
)
bundles_path = "/dl/pool/AssetBundles"
default_ver = 10063200
max_test_amount = 30
test_multiplier = 10

ver = default_ver
i = 0
while i < max_test_amount:
    guess = ver + i * test_multiplier
    url = f"http://{host}{manifest_path % guess}"
    try:
        response = urllib.request.urlopen(url)
        if response.code == 200:
            ver = guess
            i = 0
    except urllib.error.HTTPError:
        pass
    i += 1
print(ver)
urllib.request.urlretrieve(f"http://{host}{masterdata_path % ver}", "masterdata")

cdb_path = "master.cdb"
db_path = "master.db"
db_raw_path = "master_raw.db"
with open("masterdata") as fd:
    hash_ = fd.readline().split(",")[2]
    urllib.request.urlretrieve(
        f"http://{host}{bundles_path}/{hash_[:2]}/{hash_}", cdb_path
    )

stream = os.popen(f"Coneshell_call.exe -cdb {cdb_path} {db_path}")
output = stream.read()
print(output)

os.remove("masterdata")
os.remove("master.cdb")
copy(db_path, db_raw_path)

conn = sqlite3.connect(db_path)


def clean_db(conn: sqlite3.Connection, lookup: dict[str, dict]):
    c = conn.cursor()

    data = c.execute("select name from sqlite_master where type='table'").fetchall()
    table_names = [t for (t, *_) in data if t.startswith("v1")]

    whitelist = [
        "clan_battle_2_map_data",
        "clan_battle_period",
        "wave_group_data",
        "enemy_parameter",
        "clan_battle_period",
        "unit_data",
        "unit_enemy_data",
    ]

    for table in table_names:
        if not lookup.get(table, {}).get("name") in whitelist:
            continue

        query = ""
        for k, v in lookup[table]["cols"].items():
            query += f"alter table {table} rename column '{k}' to '{v}';"
        query += f"alter table {table} rename to {lookup[table]['name']};"
        c.executescript(query)
    conn.commit()


with open("lookup_table.json", "r", encoding="utf-8") as fp:
    lt = json.load(fp)
clean_db(conn, lt)
