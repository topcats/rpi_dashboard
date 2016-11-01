import os
import ConfigParser


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')
config = ConfigParser.RawConfigParser()
config.read('eClock.cfg')

def dovalue(nsection,nkey,nprompt):
    if config.has_section(nsection) == False:
        config.add_section(nsection)
    if config.has_option(nsection,nkey) == False:
        config.set(nsection,nkey,'')
    newvalue = raw_input(nprompt+' ['+config.get(nsection,nkey)+'] ?') or config.get(nsection,nkey)
    config.set(nsection,nkey,newvalue)


print 'Raspberry PI Dash Display Setup'
print 'from https://github.com/topcats/rpi_dashboard'
print ''

print 'Setup config (y) ?'
nully = raw_input('')
if (nully ==  '' or nully == 'y'):
    #all ok
    print ''
else:
    quit()

#Set Weather Stuff
print 'Weather:'
dovalue('Weather','appid','App ID')
dovalue('Weather','TownID','Town ID')
dovalue('Weather','TownName','Town Name')
dovalue('Weather','Refresh','Refresh interval (minutes)')

#DLNA
print 'DLNA'
dovalue('DLNA','url','MiniDLNA Web Address')
dovalue('DLNA','Refresh','Refresh interval (minutes)')

#User Stuff
print 'Owner'
dovalue('Owner','PhoneIP','Phone IP Address')
dovalue('Owner','CheckInterval','Check interval (seconds)')


#Office 365
print 'Office 365'
dovalue('Office365','email','Email Address')
dovalue('Office365','password','Password')
dovalue('Office365','Refresh','Refresh interval (minutes)')



#Save it
print ''
print 'New Config'
for section in config.sections():
    print section
    for key, val in config.items(section):
        print '    '+key+ "\t = " + val
nully = raw_input('All Ok (Enter y to save) ?')
if (nully == 'y'):
    with open('eClock.cfg', 'wb') as configfile:
        config.write(configfile)
    print 'Saved'
