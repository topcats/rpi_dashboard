import os
import ConfigParser
import socket
from Crypto.Cipher import AES


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')
configsave = ConfigParser.RawConfigParser()
configsave.read('eClock.cfg')

def dovalue(nsection, nkey, nprompt):
    """Double checks the INI section is valid, creates if needed. Then prompts for value"""
    if configsave.has_section(nsection) == False:
        configsave.add_section(nsection)
    if configsave.has_option(nsection, nkey) == False:
        configsave.set(nsection, nkey, '')
    newvalue = raw_input(nprompt+' ['+configsave.get(nsection, nkey)+'] ? ') or configsave.get(nsection, nkey)
    configsave.set(nsection, nkey, newvalue)


def dovaluepwd(nsection, nkey, nprompt):
    """The Crypto Verion of dovalue """
    mypihostname = socket.gethostname().zfill(16)
    mypiserial = getserial().zfill(16)
    cipherobj = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    cipherobjb = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    if configsave.has_section(nsection) == False:
        configsave.add_section(nsection)
    if configsave.has_option(nsection, nkey) == False:
        configsave.set(nsection, nkey, '')
        oldvalue = ''
    else:
        oldvalue = cipherobj.decrypt(configsave.get(nsection, nkey))
    newvalue = raw_input(nprompt+' [########] ? ') or oldvalue
    configsave.set(nsection, nkey, cipherobjb.encrypt(newvalue))


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


print 'Raspberry PI Dash Display Setup'
print 'from https://github.com/topcats/rpi_dashboard'
print ''

print 'Setup config (y) ?'
nulyi = raw_input('')
if nulyi ==  '' or nulyi == 'y':
    #all ok
    print ''
else:
    quit()

#Set Weather Stuff
print 'Weather:'
dovalue('Weather', 'appid', 'App ID')
dovalue('Weather', 'TownID', 'Town ID')
dovalue('Weather', 'TownName', 'Town Name')
dovalue('Weather', 'Refresh', 'Refresh interval (minutes)')

#DLNA
print 'DLNA'
dovalue('DLNA', 'url', 'MiniDLNA Web Address')
dovalue('DLNA', 'Refresh', 'Refresh interval (minutes)')

#User Stuff
print 'Owner'
dovalue('Owner', 'PhoneIP', 'Phone IP Address')
dovalue('Owner', 'CheckInterval', 'Check interval (seconds)')


#Office 365
print 'Office 365'
dovalue('Office365', 'email', 'Email Address')
dovaluepwd('Office365', 'password', 'Password')
dovalue('Office365', 'Refresh', 'Refresh interval (minutes)')



#Save it
print ''
print 'New Config'
for section in configsave.sections():
    print section
    for key, val in configsave.items(section):
        print '    '+key+ "\t = " + val
nulyi = raw_input('All Ok (Enter y to save) ?')
if nulyi == 'y':
    with open('eClock.cfg', 'wb') as configfile:
        configsave.write(configfile)
    print 'Saved'
