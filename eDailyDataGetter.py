#!/usr/bin/python3
# rpi_dashboard
# =================
# Data Getter - Daily runner

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import json
import datetime as dt
import base64



# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

from infosource.app_webcal import app_webcal

with open('conf/o365.json') as fp:
    json_o365config = json.load(fp)
with open('conf/site.json') as fp:
    json_siteconfig = json.load(fp)

owebcalaction = app_webcal()
json_site = json_siteconfig["locations"][1]
if json_site is None:
    print("ERROR: site not found")
else:
    print("SITE: " + json_site["id"])
    print("    : " + json_site["name"])

    if not 'calendar' in json_site:
         json_site["calendar"] = {}
    if not 'webcal_source' in json_site["calendar"]:
         json_site["calendar"]["webcal_source"] = []

    for webcalsource in json_site["calendar"]["webcal_source"]:
        print("      - " + webcalsource['title'])
        cal_output = owebcalaction.process(webcalconfig=webcalsource)
        if cal_output is None or not 'events' in cal_output:
            print("ERROR: no webcal returned")
        else:
            for webevent in cal_output['events']:
                print("        " + str(dt.datetime.fromtimestamp(webevent['Start'])) + " - " + webevent['Subject'])
                webevent_json = json.dumps(webevent)
                base64_bytes = base64.b64encode(webevent_json.encode("utf-8"))
                base64_string = base64_bytes.decode("utf-8")
                # print(base64_string)
                os.system('php -f alternate/eClockDataUpdate.php ' + json_site["id"] + ' ' + base64_string)
        print()

print()
