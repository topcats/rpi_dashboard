#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import shutil
import glob
import json
import time
import datetime as dt

print("TEST - Photo HEIC")

# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

from infosource.app_photo import app_photo

with open('conf/o365.json', encoding='utf-8') as fp:
    json_config = json.load(fp)
with open('conf/site.json', encoding='utf-8') as fp:
    json_siteconfig = json.load(fp)

o365action = app_photo(config=json_config)
json_site = json_siteconfig["locations"][1]


print(json_site["id"])
print(json_site["photo"])

o365datajson = o365action.process(siteconfig=json_site['photo'], locationid=json_site["id"])

print(o365datajson)
