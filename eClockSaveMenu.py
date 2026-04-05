#!/usr/bin/python3
# rpi_dashboard
# =================
# Data Update - Menu Changes
# 1. Check for new menu item file
# 2. If exists read in and update Excel
# 3. Update local menu file
# 4. Post to Teams Chat

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import time

# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

# Import Menu app
from infosource.app_menu import *


def fnSaveO365Menu():
    """
    Save Office365 Info Pane Dinner Menu information

    Cycles round all locations and looks for updated files
    """

    # Open Config
    with open('conf/site.json', encoding='utf-8') as fp:
        json_siteconfig = json.load(fp)

    # Loop round all site locations and get data
    o365actionmenu = app_menu()
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
            with open(newfilename, encoding='utf-8') as fp:
                json_newmenuitem = json.load(fp)

            if json_newmenuitem is not None:
                newItem = DinnerMenuItem()
                newItem.dinneroption = str(json_newmenuitem['meal'])
                newItem.chef = str(json_newmenuitem['chef'])
                newItem.ingredients = str(json_newmenuitem['ingredients'])
                newItem.rowindex = json_newmenuitem['rid']

                # Update Remote Excel
                actionOutput = o365actionmenu.PutNewItem(sitemenuconfig=json_site['menu'], menuitem=newItem)

                # Remote Update all good
                if actionOutput:
                    # Update Local file
                    o365actionmenu.SaveNewItem(siteid=json_site["id"], sitemenuconfig=json_site['menu'], menuitem=newItem, author=str(json_newmenuitem['modifiedby']))

                    # Post Announce
                    o365actionmenu.NotifyNewItem(sitemenuconfig=json_site['menu'], menuitem=newItem)

                    # Remove file if done
                    os.remove(newfilename)
                else:
                    print("Error updating menu item to Excel for site "+json_site["id"])
            else:
                print("Error reading new menu item file for site "+json_site["id"])
        else:
            print("Skipped: No new menu item file for site "+json_site["id"])


#######################################
# Main program
# fnGetO365Menu()

# 1 Check any to process (all sites)
# 2 read new entry
# 3 update excel
# 4 update local
# 5 post to teams chat

fnSaveO365Menu()
