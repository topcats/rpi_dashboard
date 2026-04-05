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
import base64

print("TEST - WebCal")

# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')

from infosource.app_webcal import app_webcal

with open('conf/o365.json', encoding='utf-8') as fp:
    json_o365config = json.load(fp)
with open('conf/site.json', encoding='utf-8') as fp:
    json_siteconfig = json.load(fp)

owebcalaction = app_webcal()
json_site = json_siteconfig["locations"][1]


print(json_site["id"])
#print(json_site["calendar"])
#print(json_site["calendar"]["webcal_source"][0])
print()
cal_output = owebcalaction.process(webcalconfig=json_site["calendar"]["webcal_source"][7])
#print(cal_output)

#for webevent in cal_output['events']:
#    print(webevent['Subject'])
#    webevent_json = json.dumps(webevent)
#    base64_bytes = base64.b64encode(webevent_json.encode("utf-8"))
#    base64_string = base64_bytes.decode("utf-8")
#    print(base64_string)

webevent = cal_output['events'][0]
print("ID", webevent['Id'])
print("Subject", webevent['Subject'])
print(webevent['Start'], time.localtime(webevent['Start']))

# webevent_json = json.dumps(webevent)
# base64_bytes = base64.b64encode(webevent_json.encode("utf-8"))
# base64_string = base64_bytes.decode("utf-8")
# print(base64_string)

# os.system('php -f alternate/eClockDataUpdate.php ' + json_site["id"] + ' ' + base64_string)
