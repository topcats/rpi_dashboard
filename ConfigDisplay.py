#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

# IMPORTS
from disp.conf import disp_conf
from util.helper_coding import helper_coding

# GLOBAL VARIABLES
CONFIG_FILENAME = 'conf/display.json'

# Sub Main for Config
DISP_CONFIG = disp_conf(CONFIG_FILENAME).loadConfig()


def doValueBool(section, key, prompt):
    global DISP_CONFIG
    if key is None:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = ''
        existingValue = DISP_CONFIG[section]
    else:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = {}
        if not key in DISP_CONFIG[section]:
            DISP_CONFIG[section][key] = None
        existingValue = DISP_CONFIG[section][key]

    newvalue = bool(input(prompt+' ['+str(existingValue)+'] ? ') or existingValue) or None
    if key is None:
        DISP_CONFIG[section] = newvalue
    else:
        DISP_CONFIG[section][key] = newvalue


def doValueInt(section, key, prompt):
    global DISP_CONFIG
    if key is None:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = ''
        existingValue = DISP_CONFIG[section]
    else:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = {}
        if not key in DISP_CONFIG[section]:
            DISP_CONFIG[section][key] = None
        existingValue = DISP_CONFIG[section][key]

    newvalue = int(input(prompt+' ['+str(existingValue)+'] ? ') or existingValue) or None
    if key is None:
        DISP_CONFIG[section] = newvalue
    else:
        DISP_CONFIG[section][key] = newvalue


def doValueStr(section, key, prompt):
    global DISP_CONFIG
    if key is None:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = ''
        existingValue = DISP_CONFIG[section]
    else:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = {}
        if not key in DISP_CONFIG[section]:
            DISP_CONFIG[section][key] = None
        existingValue = DISP_CONFIG[section][key]
    # Process Input
    existingValueDisp = existingValue if existingValue is not None else ''
    newvalue = input(prompt+' ['+existingValueDisp+'] ? ') or existingValue
    if key is None:
        DISP_CONFIG[section] = newvalue
    else:
        DISP_CONFIG[section][key] = newvalue


def doValuePwd(section, key, prompt):
    global DISP_CONFIG
    if key is None:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = ''
        existingValue = DISP_CONFIG[section]
    else:
        if not section in DISP_CONFIG:
            DISP_CONFIG[section] = {}
        if not key in DISP_CONFIG[section]:
            DISP_CONFIG[section][key] = None
        existingValue = DISP_CONFIG[section][key]
    try:
        decryptedpassword = helper_coding().decode(existingValue)
    except Exception as ex:
        print("- Unable to read encrypted value")
        decryptedpassword = ""
    # Process Input
    newvalue = input(prompt+' [########] ? ') or decryptedpassword
    newvalueencode = helper_coding().encode(newvalue)
    if key is None:
        DISP_CONFIG[section] = newvalueencode
    else:
        DISP_CONFIG[section][key] = newvalueencode



print('Raspberry PI Dash Display Setup')
print('from https://github.com/topcats/rpi_dashboard')
print()

print('Setup config (y) ?')
nulyi = input('')
if nulyi ==  '' or nulyi == 'y':
    #all ok
    print('')
else:
    quit()

#Set Weather Stuff
print('Weather:')
doValueInt('weather', None, 'Town ID')


#Z-Wave
print('Z-Wave')
doValueBool('zwave', 'enabled', 'Z-Wave Control Enabled (0 will disable)')
doValueStr('zwave', 'url', 'Automation API Base URL Address')
doValueStr('zwave', 'username', 'Username')
doValuePwd('zwave', 'password', 'Password')
doValueStr('zwave', 'tag', 'Device Tag')


#Save it
print()
print('New Config')
nulyi = input('All Ok (Enter y to save) ?')
if nulyi == 'y':
    disp_conf(CONFIG_FILENAME).saveConfig(DISP_CONFIG)
    print('Saved')
