# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import time
import os
import shutil
import ConfigParser
import socket
from O365 import *
from Crypto.Cipher import AES


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')
config = ConfigParser.ConfigParser()
config.read('eClock.cfg')

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


def fnGetWeather():
    """Get Weather Infomation from OpenWeatherMap"""
    if int(config.get('Weather', 'Refresh')) == 0:
        if os.path.isfile('data_weather.txt'):
            shutil.copyfile('data_weather.txt', 'data_weather.old.txt')
            os.remove('data_weather.txt')
        if os.path.isfile('data_forcast.txt'):
            shutil.copyfile('data_forcast.txt', 'data_forcast.old.txt')
            os.remove('data_forcast.txt')
    
    else:
        try:
            with open('data_weather.txt') as fp:
                json_obj = json.load(fp)
            data_timediff = int(time.time()) - int(json_obj['dt'])

        except:
            data_timediff = int(config.get('Weather', 'Refresh'))*61
    
        try:
            if os.path.isfile('data_weather.txt'):
                shutil.copyfile('data_weather.txt', 'data_weather.old.txt')
            if os.path.isfile('data_forcast.txt'):
                shutil.copyfile('data_forcast.txt', 'data_forcast.old.txt')
            if data_timediff >= (int(config.get('Weather', 'Refresh'))*60):
                #http://openweathermap.org/current#parameter
                #Ashburton:2656977
                #Downham Market:2651030
                # Get Weather, check for name and get icon image
                url_to_call = 'http://api.openweathermap.org/data/2.5/weather?id='+config.get('Weather', 'TownID')+'&appid='+config.get('Weather', 'appid')+'&units=metric'
                response = urllib2.urlopen(url_to_call)
                json_obj = json.load(response)
                with open('data_weather.txt', 'w') as fp:
                    json.dump(json_obj, fp)
                
                if str(json_obj['name']) <> config.get('Weather', 'TownName'):
                    raise Exception("Incorrect Location")
                time.sleep(1)
                
                fnGetWeatherIcon(json_obj['weather'][0]['icon'], 'weather')
                
                url_to_call = 'http://api.openweathermap.org/data/2.5/forecast?id='+config.get('Weather', 'TownID')+'&appid='+config.get('Weather', 'appid')+'&units=metric'
                response = urllib2.urlopen(url_to_call)
                json_obj = json.load(response)
                with open('data_forcast.txt', 'w') as fp:
                    json.dump(json_obj, fp)
                
                if str(json_obj['city']['name']) <> config.get('Weather', 'TownName'):
                    raise Exception("Incorrect Forcast Location")
                time.sleep(1)

                fnGetWeatherIcon(json_obj['list'][0]['weather'][0]['icon'], 'forcast1')
                fnGetWeatherIcon(json_obj['list'][1]['weather'][0]['icon'], 'forcast2')
                fnGetWeatherIcon(json_obj['list'][2]['weather'][0]['icon'], 'forcast3')
                fnGetWeatherIcon(json_obj['list'][3]['weather'][0]['icon'], 'forcast4')
                fnGetWeatherIcon(json_obj['list'][4]['weather'][0]['icon'], 'forcast5')
        
        except Exception as z:
            print 'Error:fnGetWeather', z
            if os.path.isfile('data_weather.old.txt'):
                shutil.copyfile('data_weather.old.txt', 'data_weather.txt')
            if os.path.isfile('data_forcast.old.txt'):
                shutil.copyfile('data_forcast.old.txt', 'data_forcast.txt')


def fnGetWeatherIcon(value, target):
    """Downloads Weather Icon image file"""
    try:
        if os.path.isfile('icon_'+target+'.png'):
            shutil.copyfile('icon_'+target+'.png', 'icon_'+target+'.old.png')
        
        weatherimage_url = 'http://openweathermap.org/img/w/'+str(value)+'.png'
        urllib.urlretrieve(weatherimage_url, 'icon_'+target+'.png')
        time.sleep(1)
    
    except Exception as z:
        print 'Error:fnGetWeatherIcon', z
        if os.path.isfile('icon_'+target+'.old.png'):
            shutil.copyfile('icon_'+target+'.old.png', 'icon_'+target+'.png')


def fnGetDlna():
    """Get miniDLNA Information"""
    if int(config.get('DLNA', 'Refresh')) == 0:
        if os.path.isfile('data_dlna.txt'):
            shutil.copyfile('data_dlna.txt', 'data_dlna.old.txt')
            os.remove('data_dlna.txt')
    
    else:
        try:
            data_timediff = int(time.time()) - int(os.path.getmtime('data_dlna.txt'))
        except:
            data_timediff = int(config.get('DLNA', 'Refresh'))*61
        
        try:
            if os.path.isfile('data_dlna.txt'):
                shutil.copyfile('data_dlna.txt', 'data_dlna.old.txt')
            if data_timediff >= (int(config.get('DLNA', 'Refresh'))*60):
                url_to_call = 'http://'+config.get('DLNA', 'url')+'/'
                response = urllib2.urlopen(url_to_call)
                response_data = response.read()
                count_video = response_data.index("Video")
                count_videoe = response_data.index('</tr>', count_video)
                value_video = response_data[count_video:count_videoe]
                value_video = value_video.replace('Video files</td><td>', '')
                value_video = value_video.replace('</td>', '')
                count_audio = response_data.index("Audio")
                count_audioe = response_data.index('</tr>', count_audio)
                value_audio = response_data[count_audio:count_audioe]
                value_audio = value_audio.replace('Audio files</td><td>', '')
                value_audio = value_audio.replace('</td>', '')
                value_updated = int(time.time())
                
                if int(value_audio) <= 0:
                    raise Exception("No Audio??")
                
                data = {'audio':value_audio, 'video':value_video, 'updated':value_updated}
                with open('data_dlna.txt', 'w') as fp:
                    json.dump(data, fp)
        
        except:
            print 'Error:fnGetDlna'
            if os.path.isfile('data_dlna.old.txt'):
                shutil.copyfile('data_dlna.old.txt', 'data_dlna.txt')


def fnGetO365Calendar():
    '''Get Office365 Calendar information'''
    if int(config.get('Office365', 'Refresh')) == 0:
        if os.path.isfile('data_o365calendar.txt'):
            shutil.copyfile('data_o365calendar.txt', 'data_o365calendar.old.txt')
            os.remove('data_o365calendar.txt')
    
    else:
        try:
            with open('data_o365calendar.txt') as fp:
                json_obj = json.load(fp)
            data_timediff = int(time.time()) - int(json_obj['dt'])
        except:
            data_timediff = int(config.get('Office365', 'Refresh'))*61
        
        try:
            if os.path.isfile('data_o365calendar.txt'):
                shutil.copyfile('data_o365calendar.txt', 'data_o365calendar.old.txt')
            if data_timediff >= (int(config.get('Office365', 'Refresh'))*60):
                
                mypihostname = socket.gethostname().zfill(16)
                mypiserial = getserial().zfill(16)
                cipherobj = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
                o365_authentication = (config.get('Office365', 'email'), cipherobj.decrypt(config.get('Office365', 'password')))
                o365_schedule = Schedule(o365_authentication)
                o365_result = o365_schedule.getCalendars()
                timethismorning = time.time()
                timethismorning = time.gmtime(timethismorning)
                timethismorning = time.strftime(Calendar.timemorning_string, timethismorning)
                timeendmorning = time.strptime(timethismorning, Calendar.time_string)
                timeendmorning = int(time.strftime('%s', timeendmorning))
                timeendmorning += 3600*24*200
                timeendmorning = time.gmtime(timeendmorning)
                timeendmorning = time.strftime(Calendar.time_string, timeendmorning)
                json_outs = {}
                json_outs['dt'] = int(time.time())
                o365_bookings = []

                for o365_cal in o365_schedule.calendars:
                    o365_result = o365_cal.getEvents(timethismorning, timeendmorning, 100)
                    for o365_event in o365_cal.events:
                        o365_bookings.append(fnGetO365Calendar_processcategory(o365_event.fullcalendarsavejson()))

                o365_bookings = sorted(o365_bookings, key = lambda x: (x['Start'], x['End']))
                json_outs[config.get('Office365', 'email')] = o365_bookings

                with open('data_o365calendar.txt', 'w') as outs:
                    json.dump(json_outs, outs)
            
        except:
            print 'Error:fnGetO365Calendar'
            if os.path.isfile('data_o365calendar.old.txt'):
                shutil.copyfile('data_o365calendar.old.txt', 'data_o365calendar.txt')


def fnGetO365Calendar_processcategory(calitem):
    '''Merge Office365 Calendar Category Information'''
    calcols = CatColors()
    with open('data_o365mastercategorylist.txt') as fp:
        json_objcat = json.load(fp)
    officecategory = Category(json_objcat)

    newcategories = {}
    for catitem in calitem['Categories']:
        newcategoriesitem = {}
        catcolitem = calcols.get_item_fromid(officecategory.get_colorid_fromname(catitem))
        newcategoriesitem['colorid'] = catcolitem.colorid
        newcategoriesitem['hex'] = catcolitem.hex
        newcategories[catitem] = newcategoriesitem

    calitem['Categories'] = newcategories
    return calitem



#main program
fnGetWeather()
fnGetDlna()
fnGetO365Calendar()
