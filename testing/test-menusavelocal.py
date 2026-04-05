#!/usr/bin/python3
# rpi_dashboard
# =================
# Test Menu Saving

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json

# MAKE SURE WE is in the correct directory
os.chdir('C:/Users/topcat/source/GitHub/rpi_dashboard')

# Import Menu app
from infosource.app_menu import *

print("open file")

configfile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf/site.json'))

print (configfile)

with open(configfile, encoding='utf-8') as fp:
    json_siteconfig = json.load(fp)

o365action = app_menu()


json_site = json_siteconfig["locations"][1]

# Test Menu item
newItem = DinnerMenuItem()
newItem.dinneroption = "Test Meal"
newItem.chef = "Test Chef"
newItem.ingredients = "Test Ingredients"
newItem.rowindex = 69

o365action.SaveNewItem(siteid=2, sitemenuconfig=json_site['menu'], menuitem=newItem, author="Testing")

