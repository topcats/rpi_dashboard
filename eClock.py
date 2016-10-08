# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
from string import capitalize
from PIL import Image, ImageTk
import time
import io
import os
try:
	# Python2
	import Tkinter as tk
	from Tkinter import Frame, Canvas
except ImportError:
	# Python3
	import tkinter as tk
	from tkinter import Frame, Canvas


def tick(tick_time1=''):
	try:
		global blnflag
		# get the current local time from the PC
		tick_time2 = time.strftime('%H:%M:%S')
		# if time string has changed, update it
		if tick_time2 != tick_time1:
			tick_time1 = tick_time2
			clock.config(text=tick_time2)
			fnGetTristanHome();
		# calls itself every 200 milliseconds
		# to update the time display as needed
		min2=tick_time2.split(':')
		if (min2[1]=='30' or min2[1]=='00') and blnflag==True:
			#Update Date and set colours
			clockdate.config(text=time.strftime('%A %d %b %Y'))
			if (min2[0]>=23 or min2[0]<=7):
				clock.config(fg='red')
				weathercanvas.itemconfig(weatherlabel, fill='#808080')
			else:
				clock.config(fg='green')
				weathercanvas.itemconfig(weatherlabel, fill='white')

			fnGetWeather()
			time.sleep(2)

			infodlna.config(text=fnGetDlnaText())
			time.sleep(2)

			blnflag = False
		elif min2[1]!='30' and min2[1]!='00':
			blnflag = True

		clock.after(200, tick)
	except:
		print 'Error'
		return 'Call updaing clock, try again'
		tick()


def fnGetWeatherStatus():
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
		else:
			with open('data_weather.txt') as fp:
				json_obj = json.load(fp)

		current_desc = capitalize(json_obj['weather'][0]['description'])
		#current_temp = kelvinToCelsius(json_obj['main']['temp'])
		current_temp = json_obj['main']['temp']
		current_icon = json_obj['weather'][0]['icon']
		current_location = json_obj['name']

		return current_desc,current_temp,current_icon,current_location

	except:
		print 'Error:fnGetWeather'
		return 'Error','Error','01n','unknown'


def fnGetWeather():
	mylist = fnGetWeatherStatus()
	#mylist = ['skipped','skip','default.png']
	#local_encoding = 'cp850'
	#deg = u'\xb0'.encode(local_encoding)
	#sub= "°C.".decode('utf8').encode(local_encoding)
	weatherimage_url = 'http://openweathermap.org/img/w/'+str(mylist[2]+'.png')
	#response = urllib2.urlopen(weatherimage_url)
	#weatherimage_file = io.BytesIO(response.read())
	#weatherimage = Image.open(weatherimage_file)
	#weatherphoto = tk.PhotoImage(weatherimage)
	#weathericon.config(image=weatherphoto)
	#weathericon.config(photo=weatherphoto)
	#weathericon.image = weatherphoto # keep a reference!
	#imgcanvas = Canvas(weatherfr, bg="green", width=200, height=200)
	#imgcanvas.pack(side='left')

	urllib.urlretrieve(weatherimage_url,'/home/pi/dashdisplay/current.png')
	time.sleep(2)

	#photoimg = tk.PhotoImage(file="default.png")
	#imgcanvas.create_image(150, 150, image=photoimg)
	weatherimgsrc = Image.open("current.png")
	weatherimgphoto = ImageTk.PhotoImage(weatherimgsrc)
	#weathercanvas.delete(weathernowimage)
	#weathernowimage = weathercanvas.create_image(30, 30, image=weatherimgphoto)

	weathercanvas.itemconfig(weatherlabel, text='Weather (' + str(mylist[3]) + ') : '+"\n"+ str(mylist[0])+" : : "+ str(mylist[1]) + " °c")



def fnGetDlnaStatus():
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
		else:
			with open('data_dlna.txt') as fp:
				data = json.load(fp)
				value_audio = data['audio']
				value_video = data['video']

		return value_video,value_audio

	except:
		print 'Error:fnGetDlnaStatus'
		return 'err', 'err'


def fnGetDlnaText():
	mydlna = fnGetDlnaStatus()
	return 'DLNA Status: '+"\n"+ 'VID:'+mydlna[0]+'  MP3:'+mydlna[1]

def fnGetTristanHome():
	response = os.system('ping -c 1 -w1 wp8_tristancole')
	if response == 0:
		#yes in
		bCloser.config(fg='green')
	else:
		bCloser.config(fg='red')
		

def fnCloseNow():
	print 'Closing now...'
	root.destroy()
	time.sleep(1)
	#sys.exit()



#main program
root = tk.Tk()
root.attributes("-fullscreen",True)
root.config(cursor="none")
root.config(background="black")

#Close Button
bCloser = tk.Button(root, text='X', fg='red', bg='black', command=fnCloseNow)
bCloser.pack(side='right')

clock = tk.Label(root, font=('times', 50, 'bold'), fg='green',bg='black')
clockdate = tk.Label(root, font=('times', 30, 'bold'), fg='#ff6666', bg='black', text=time.strftime('%A %d %b %Y'))

#weatherfr = tk.Frame(root, bg='black')
#weatherlabel = tk.Label(weatherfr,font=('times', 30), fg='white',bg='black')
#weathericon = tk.Label(weatherfr,bg='white',bd=0,compound='center',height=32,padx=0,pady=0,width=32)
#weathericon.pack(side='left')
#weatherlabel.pack(fill='both', expand=1)


weathercanvas = Canvas(root, bg="black", width=300, height=150, borderwidth=0)

weatherimgsrc = Image.open("default.png")
weatherimgphoto = ImageTk.PhotoImage(weatherimgsrc)
weathernowimage = weathercanvas.create_image(30, 30, image=weatherimgphoto)

weatherlabel = weathercanvas.create_text(300,46, font=('times', 26), fill='white', justify='center', text='Weather Info')

#weatherfd = urllib2.urlopen("http://openweathermap.org/img/w/01n.png")
#weatherimage_file = io.BytesIO(weatherfd.read())
#weatherimage = Image.open(weatherimage_file)
#weatherphoto = ImageTk.PhotoImage(weatherimage)
#weather.config(text='Weather loading ...'+weatherphoto)

infodlna=tk.Label(root,font=('times', 20), fg='blue',bg='black')

clock.pack(fill='both', expand=1)
clockdate.pack(fill='both', expand=1)
weathercanvas.pack(fill='both')
#weatherfr.pack(fill='both', expand=1)
infodlna.pack(fill='both',expand=1)
blnflag = True

fnGetWeather()
infodlna.config(text=fnGetDlnaText())

tick()
root.mainloop()

