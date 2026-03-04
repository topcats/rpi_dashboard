#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time
import datetime as dt

print("TEST - Calendar Infopane")

# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

from infosource.app_calendar import app_calendar

with open('conf/o365.json') as fp:
    json_config = json.load(fp)
with open('conf/site.json') as fp:
    json_siteconfig = json.load(fp)

o365action = app_calendar(config=json_config)

json_site = json_siteconfig["locations"][0]


print(json_site["id"])
print(json_site["calendar"])
print()
json_output = o365action.process(siteconfig=json_site['calendar'])

print(json_output)
