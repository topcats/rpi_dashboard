#!/usr/bin/python3
import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")
import os
import configparser
import socket
import base64
from Crypto.Cipher import AES
from O365 import *
import json
import time


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')
configsave = configparser.ConfigParser()
configsave.read('eClocktest.cfg')

def dovalue(nsection, nkey, nprompt):
    """Double checks the INI section is valid, creates if needed. Then prompts for value"""
    if configsave.has_section(nsection) == False:
        configsave.add_section(nsection)
    if configsave.has_option(nsection, nkey) == False:
        configsave.set(nsection, nkey, '')
    newvalue = input(nprompt+' ['+configsave.get(nsection, nkey)+'] ? ') or configsave.get(nsection, nkey)
    configsave.set(nsection, nkey, newvalue)


def dovaluepwd(nsection, nkey, nprompt):
    """The Crypto Verion of dovalue """
    mypihostname = str.encode(socket.gethostname().zfill(16))
    mypiserial = str.encode(getserial().zfill(16))
    cipherobj = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    cipherobjb = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    oldvalue = ''
    if configsave.has_section(nsection) == False:
        configsave.add_section(nsection)
    if configsave.has_option(nsection, nkey) == False:
        configsave.set(nsection, nkey, '')
    else:
        if configsave.get(nsection, nkey) != '':
            oldvalue = configsave.get(nsection, nkey)
            oldvalue = base64.b64decode(str.encode(oldvalue))
            oldvalue = cipherobj.decrypt(oldvalue).decode('UTF-8')
    newvalue = input(nprompt+' [########] ? ') or oldvalue
    newvalue = cipherobjb.encrypt(str.encode(newvalue))
    newvalue = base64.b64encode(newvalue).decode('UTF-8')
    configsave.set(nsection, nkey, newvalue)


def getserial():
    """Extract serial from cpuinfo file"""
    cpuserial = "0000000000000000"
    try:
        gsfile = open('/proc/cpuinfo', 'r')
        for line in gsfile:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        gsfile.close()
    except:
        cpuserial = "ERROR000000000"
    return cpuserial


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
dovalue('Weather', 'Refresh', 'Refresh interval (minutes) (0 will disable)')
dovalue('Weather', 'appid', 'App ID')
dovalue('Weather', 'TownID', 'Town ID')
dovalue('Weather', 'TownName', 'Town Name')

#DLNA
print('DLNA')
dovalue('DLNA', 'Refresh', 'Refresh interval (minutes) (0 will disable)')
dovalue('DLNA', 'Type', 'DLNA Server Type, 1 = MiniDLNA, 2 = Serviio')
dovalue('DLNA', 'url', 'DLNA URI Address (exclude port)')

#User Stuff
print('Owner')
dovalue('Owner', 'CheckInterval', 'Check interval (seconds) (0 will disable)')
dovalue('Owner', 'PhoneIP', 'Phone IP Address')

#Office 365
print('Office 365')
dovalue('Office365', 'Refresh', 'Refresh interval (minutes) (0 will disable)')
dovaluepwd("Office365", 'ClientSecret', 'Azure Client Secret Key')
dovalue('Office365', 'email', 'Email Address')


#Z-Wave
print('Z-Wave')
dovalue('ZWave', 'enabled', 'Z-Wave Control Enabled (0 will disable)')
dovalue('ZWave', 'url', 'Automation API Base URL Address')
dovalue('ZWave', 'username', 'Username')
dovaluepwd('ZWave', 'password', 'Password')


#Save it
print()
print('New Config')
for section in configsave.sections():
    print(section)
    for key, val in configsave.items(section):
        print('    '+key+ "\t = " + val)
nulyi = input('All Ok (Enter y to save) ?')
if nulyi == 'y':
    with open('eClocktest.cfg', 'w') as configfile:
        configsave.write(configfile)
    print('Saved')


#Check 0365 Auth
#Also grab Master Category list
if int(configsave.get('Office365', 'Refresh')) != 0:
    o365_cipherobj = AES.new(str.encode(socket.gethostname().zfill(16)), AES.MODE_CFB, str.encode(getserial().zfill(16)))
    o365_clientsecret = configsave.get('Office365', 'ClientSecret')
    o365_clientsecret = base64.b64decode(str.encode(o365_clientsecret))
    o365_clientsecret = o365_cipherobj.decrypt(o365_clientsecret).decode('UTF-8')
    #'6GZNl1wp2ZyXe/+0.ZaZCaAt_sR7DCsL'
    o365_tokenbackend = FileSystemTokenBackend(token_path='data/', token_filename='o365_token.json')
    o365_mycredentials = ('', o365_clientsecret)
    o365_account = Account(o365_mycredentials)

    if not o365_account.is_authenticated:  # will check if there is a token and has not expired
        myscopes = ['basic', 'calendar_shared_all', 'MailboxSettings.Read']
        # ask for a login
        print('O365 not currently authed, login please')
        print('  Copy the url below into a web browser, login to you Office365 Account.')
        print('  Once logged in you will return a blank page, copy the URL and past back here.')
        print()
        o365_account.authenticate(scopes=myscopes)

    if not o365_account.is_authenticated:  # will check if there is a token and has not expired
        sys.exit('0365 Not Authenticated!! -- STOP')

    #Save Master Category List
    usrsettings = o365_account.settings()
    json_catouts = {}
    json_catouts['dt'] = int(time.time())
    json_catouts['MasterList'] = usrsettings.get_categories()
    with open('data_o365mastercategorylist.txt', 'w') as outs:
        json.dump(json_catouts, outs)
    print('O365 Master Category list saved')
