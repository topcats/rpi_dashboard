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

print("TEST - O365 Menu")

# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

from infosource.app_menu import app_menu

with open('conf/o365.json', encoding='utf-8') as fp:
    json_config = json.load(fp)
with open('conf/site.json', encoding='utf-8') as fp:
    json_siteconfig = json.load(fp)

o365action = app_menu(config=json_config)

json_site = json_siteconfig["locations"][1]


print(json_site["id"])
# print(json_site["menu"])
print()

json_menuoptions = o365action.getEditOptions(siteconfig=json_site['menu'])
o365action.getRecipeOptions(json_site["id"], json_menuoptions['option'])
#print(json_menuoptions)