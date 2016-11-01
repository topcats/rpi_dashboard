# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import time
import os
import shutil
import ConfigParser


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')
config = ConfigParser.ConfigParser()
config.read('eClock.cfg')


def fnGetWeather():
	data_timediff = int(config.get('Weather','Refresh'))*60
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('data_weather.txt'))
	except:
		data_timediff = int(config.get('Weather','Refresh'))*61
	
	try:
		if os.path.isfile ('data_weather.txt'): shutil.copyfile ('data_weather.txt', 'data_weather.old.txt')
		if os.path.isfile ('data_forcast.txt'): shutil.copyfile ('data_forcast.txt', 'data_forcast.old.txt')
		if (data_timediff >= (int(config.get('Weather','Refresh'))*60)):
			#http://openweathermap.org/current#parameter
			#Ashburton:2656977
			#Downham Market:2651030
			# Get Weather, check for name and get icon image
			url_to_call = 'http://api.openweathermap.org/data/2.5/weather?id='+config.get('Weather','TownID')+'&appid='+config.get('Weather','appid')+'&units=metric'
			response = urllib2.urlopen(url_to_call)
			json_obj = json.load(response)
			with open('data_weather.txt','w') as fp:
				json.dump(json_obj, fp)
			
			if str(json_obj['name']) <> config.get('Weather','TownName'):
				raise Exception("Incorrect Location")
			time.sleep(1)
			
			fnGetWeatherIcon(json_obj['weather'][0]['icon'], 'weather')
			
			url_to_call = 'http://api.openweathermap.org/data/2.5/forecast?id='+config.get('Weather','TownID')+'&appid='+config.get('Weather','appid')+'&units=metric'
			response = urllib2.urlopen(url_to_call)
			json_obj = json.load(response)
			with open('data_forcast.txt','w') as fp:
				json.dump(json_obj, fp)
			
			if str(json_obj['city']['name']) <> config.get('Weather','TownName'):
				raise Exception("Incorrect Forcast Location")
			time.sleep(1)

			fnGetWeatherIcon(json_obj['list'][0]['weather'][0]['icon'], 'forcast1')
			fnGetWeatherIcon(json_obj['list'][1]['weather'][0]['icon'], 'forcast2')
			fnGetWeatherIcon(json_obj['list'][2]['weather'][0]['icon'], 'forcast3')
			fnGetWeatherIcon(json_obj['list'][3]['weather'][0]['icon'], 'forcast4')
			fnGetWeatherIcon(json_obj['list'][4]['weather'][0]['icon'], 'forcast5')
	
	
	except Exception as z:
		print 'Error:fnGetWeather', z
		if os.path.isfile ('data_weather.old.txt'): shutil.copyfile('data_weather.old.txt','data_weather.txt') 
		if os.path.isfile ('data_forcast.old.txt'): shutil.copyfile('data_forcast.old.txt','data_forcast.txt') 



def fnGetWeatherIcon(value,target):
	try:
		if os.path.isfile ('icon_'+target+'.png'): shutil.copyfile ('icon_'+target+'.png', 'icon_'+target+'.old.png')
		
		weatherimage_url = 'http://openweathermap.org/img/w/'+str(value)+'.png'
		urllib.urlretrieve(weatherimage_url,'icon_'+target+'.png')
		time.sleep(1)
		
	except Exception as z:
		print 'Error:fnGetWeatherIcon', z
		if os.path.isfile ('icon_'+target+'.old.png'): shutil.copyfile('icon_'+target+'.old.png','icon_'+target+'.png') 


def fnGetDlna():
	data_timediff = int(config.get('DLNA','Refresh'))*60
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('data_dlna.txt'))
	except:
		data_timediff = int(config.get('DLNA','Refresh'))*61
	
	try:
		if os.path.isfile ('data_dlna.txt'): shutil.copyfile ('data_dlna.txt', 'data_dlna.old.txt')
		if (data_timediff >= (int(config.get('DLNA','Refresh'))*60)):
			url_to_call='http://'+config.get('DLNA','url')+'/'
			response = urllib2.urlopen(url_to_call)
			response_data = response.read()
			count_video = response_data.index("Video")
			count_videoe = response_data.index('</tr>',count_video)
			value_video = response_data[count_video:count_videoe]
			value_video = value_video.replace('Video files</td><td>','')
			value_video = value_video.replace('</td>','')
			count_audio = response_data.index("Audio")
			count_audioe = response_data.index('</tr>',count_audio)
			value_audio = response_data[count_audio:count_audioe]
			value_audio = value_audio.replace('Audio files</td><td>','')
			value_audio = value_audio.replace('</td>','')
			
			if int(value_audio) <= 0:
				raise Exception("No Audio??")
			
			data = {'audio':value_audio, 'video':value_video}
			with open('data_dlna.txt','w') as fp:
				json.dump(data, fp)
	
	except:
		print 'Error:fnGetDlna'
		if os.path.isfile ('data_dlna.old.txt'):
			shutil.copyfile('data_dlna.old.txt','data_dlna.txt') 





#main program
fnGetWeather()
fnGetDlna()
