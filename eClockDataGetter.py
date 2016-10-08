# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
from string import capitalize
import time
import io
import os


def fnGetWeather():
	data_timediff = 24*3600
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('data_weather.txt'))
	except:
		data_timediff = 25*3600
	try:
		if (data_timediff >= (1700)):
			#http://openweathermap.org/current#parameter
			#Ashburton:2656977
			#Downham Market:2651030
			url_to_call = 'http://api.openweathermap.org/data/2.5/weather?id=2656977&appid=08b5e93e4e18f3bb67193ab5fa179abc&units=metric'
			response = urllib2.urlopen(url_to_call)
			json_obj = json.load(response)
			#os.rename('data_weather.txt', 'data_weatherold.txt')
			with open('data_weather.txt','w') as fp:
				json.dump(json_obj, fp)

			weatherimage_url = 'http://openweathermap.org/img/w/'+str(json_obj['weather'][0]['icon'])+'.png'
			urllib.urlretrieve(weatherimage_url,'/home/pi/dashdisplay/current.png')
	
	except:
		print 'Error:fnGetWeather'


def fnGetDlna():
	data_timediff = 24*3600
	try:
		data_timediff = int(time.time()) - int(os.path.getmtime('data_dlna.txt'))
	except:
		data_timediff = 25*3600
	try:
		if (data_timediff >= (12*3600)):
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
			data = {'audio':value_audio, 'video':value_video}
			with open('data_dlna.txt','w') as fp:
				json.dump(data, fp)

	except:
		print 'Error:fnGetDlna'




#main program
fnGetWeather()
fnGetDlna()
