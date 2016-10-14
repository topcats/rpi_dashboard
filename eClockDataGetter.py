# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import time
import os
import shutil



def fnGetWeather():
	data_timediff = 24*3600
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('/home/pi/dashdisplay/data_weather.txt'))
	except:
		data_timediff = 25*3600
	
	try:
		if os.path.isfile ('/home/pi/dashdisplay/data_weather.txt'): shutil.copyfile ('/home/pi/dashdisplay/data_weather.txt', '/home/pi/dashdisplay/data_weather.old.txt')
		if os.path.isfile ('/home/pi/dashdisplay/data_forcast.txt'): shutil.copyfile ('/home/pi/dashdisplay/data_forcast.txt', '/home/pi/dashdisplay/data_forcast.old.txt')
		if os.path.isfile ('/home/pi/dashdisplay/icon_weather.png'): shutil.copyfile ('/home/pi/dashdisplay/icon_weather.png', '/home/pi/dashdisplay/icon_weather.old.png')
		if (data_timediff >= (1700)):
			#http://openweathermap.org/current#parameter
			#Ashburton:2656977
			#Downham Market:2651030
			url_to_call = 'http://api.openweathermap.org/data/2.5/weather?id=2656977&appid=08b5e93e4e18f3bb67193ab5fa179abc&units=metric'
			response = urllib2.urlopen(url_to_call)
			json_obj = json.load(response)
			with open('/home/pi/dashdisplay/data_weather.txt','w') as fp:
				json.dump(json_obj, fp)
			
			if str(json_obj['name']) <> 'Ashburton':
				raise Exception("Incorrect Location")
			time.sleep(1)
			
			weatherimage_url = 'http://openweathermap.org/img/w/'+str(json_obj['weather'][0]['icon'])+'.png'
			urllib.urlretrieve(weatherimage_url,'/home/pi/dashdisplay/icon_weather.png')
			time.sleep(1)
			
			url_to_call = 'http://api.openweathermap.org/data/2.5/forecast?id=2656977&appid=08b5e93e4e18f3bb67193ab5fa179abc&units=metric'
			response = urllib2.urlopen(url_to_call)
			json_obj = json.load(response)
			with open('/home/pi/dashdisplay/data_forcast.txt','w') as fp:
				json.dump(json_obj, fp)
			
			if str(json_obj['city']['name']) <> 'Ashburton':
				raise Exception("Incorrect Forcast Location")
			time.sleep(1)
	
	except Exception as z:
		print 'Error:fnGetWeather', z
		if os.path.isfile ('/home/pi/dashdisplay/data_weather.old.txt'): shutil.copyfile('/home/pi/dashdisplay/data_weather.old.txt','/home/pi/dashdisplay/data_weather.txt') 
		if os.path.isfile ('/home/pi/dashdisplay/data_forcast.old.txt'): shutil.copyfile('/home/pi/dashdisplay/data_forcast.old.txt','/home/pi/dashdisplay/data_forcast.txt') 
		if os.path.isfile ('/home/pi/dashdisplay/icon_weather.old.png'): shutil.copyfile('/home/pi/dashdisplay/icon_weather.old.png','/home/pi/dashdisplay/icon_weather.png') 


def fnGetDlna():
	data_timediff = 24*3600
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('/home/pi/dashdisplay/data_dlna.txt'))
	except:
		data_timediff = 25*3600
	
	try:
		if os.path.isfile ('/home/pi/dashdisplay/data_dlna.txt'): shutil.copyfile ('/home/pi/dashdisplay/data_dlna.txt', '/home/pi/dashdisplay/data_dlna.old.txt')
		if (data_timediff >= (24*3600)):
			url_to_call='http://localhost:8200/'
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
			with open('/home/pi/dashdisplay/data_dlna.txt','w') as fp:
				json.dump(data, fp)
	
	except:
		print 'Error:fnGetDlna'
		if os.path.isfile ('/home/pi/dashdisplay/data_dlna.old.txt'):
			shutil.copyfile('/home/pi/dashdisplay/data_dlna.old.txt','/home/pi/dashdisplay/data_dlna.txt') 





#main program
fnGetWeather()
fnGetDlna()
