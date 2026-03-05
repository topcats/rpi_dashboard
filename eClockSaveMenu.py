#!/usr/bin/python3
# rpi_dashboard
# =================
# Data Update - Menu Changes

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time
import datetime as dt


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

# Import Menu app
from infosource.app_menu import *


def fnSaveO365Menu():
    '''Save Office365 Info Pane Dinner Menu information'''
    
    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)
    with open('conf/site.json') as fp:
        json_siteconfig = json.load(fp)

    # Loop round all site locations and get data
    o365action = app_menu(config=json_config)
    for json_site in json_siteconfig["locations"]:
        time.sleep(1)
        if json_site is None:
            json_site = {}
        if not 'menu' in json_site:
            json_site['menu'] = {}
        if json_site['menu'] is None:
            json_site['menu'] = {}
            json_site['menu']['refresh'] = 0
        if not 'refresh' in json_site['menu']:
            json_site['menu']['refresh'] = 0
        if not 'allowedit' in json_site['menu']:
            json_site['menu']['allowedit'] = False

        # Check new
        newfilename = 'data/web/o365_dinnermenu_new_'+json_site["id"]+'.json'
        if os.path.isfile(newfilename):
            with open(newfilename) as fp:
                json_newmenuitem = json.load(fp)

            if json_newmenuitem is not None:
                newItem = DinnerMenuItem()
                newItem.dinneroption = str(json_newmenuitem['meal'])
                newItem.chef = str(json_newmenuitem['chef'])
                newItem.ingredients = str(json_newmenuitem['ingredients'])
                newItem.rowindex = json_newmenuitem['rid']

                # Update Excel
                actionOutput = o365action.putNewItem(siteconfig=json_site['menu'], menuitem=newItem)

                # Post Announce
                if actionOutput:
                    o365action.notifyNewItem(siteconfig=json_site['menu'], menuitem=newItem)
                    # Remove file if done
                    os.remove(newfilename)



#######################################
# Main program
# fnGetO365Menu()
            
# 1 Check any to process
# 2 read new entry
# 3 update excel
# 4 post to teams chat

fnSaveO365Menu()

