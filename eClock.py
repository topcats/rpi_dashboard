# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
from string import capitalize
from PIL import Image, ImageTk
import time
import datetime
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
			# fnGetTristanHome();
		# calls itself every 200 milliseconds
		# to update the time display as needed
		min2=tick_time2.split(':')
		if (min2[1]=='32' or min2[1]=='02') and blnflag==True:
			#Update Date and set colours
			clockdate.config(text=time.strftime('%A %d %b %Y'))
			fnUpdateColor()
			fnGetWeather()
			infodlna.config(text=fnGetDlnaText())

			blnflag = False
		elif min2[1]!='32' and min2[1]!='02':
			blnflag = True

		clock.after(200, tick)
	except:
		print 'Error'
		return 'Call updaing clock, try again'
		tick()


def fnGetWeatherStatus():
	try:
		with open('data_weather.txt') as fp:
			json_obj = json.load(fp)

		current_desc = capitalize(json_obj['weather'][0]['description'])
		#current_temp = kelvinToCelsius(json_obj['main']['temp'])
		current_temp = json_obj['main']['temp']
		current_location = json_obj['name']
		current_sunlight = datetime.datetime.fromtimestamp(int(json_obj['sys']['sunrise'])).strftime('%H:%M')
		current_sunlight = current_sunlight + ' - '
		current_sunlight = current_sunlight + datetime.datetime.fromtimestamp(int(json_obj['sys']['sunset'])).strftime('%H:%M')

		return current_desc,current_temp,current_sunlight,current_location

	except:
		print 'Error:fnGetWeather'
		return 'Error','Error','00:00 - 00:00','unknown'


def fnGetWeather():
	mylist = fnGetWeatherStatus()
	#mylist = ['skipped','skip','default.png']
	#local_encoding = 'cp850'
	#deg = u'\xb0'.encode(local_encoding)
	#sub= "°C.".decode('utf8').encode(local_encoding)
	#response = urllib2.urlopen(weatherimage_url)
	#weatherimage_file = io.BytesIO(response.read())
	#weatherimage = Image.open(weatherimage_file)
	#weatherphoto = tk.PhotoImage(weatherimage)
	#weathericon.config(image=weatherphoto)
	#weathericon.config(photo=weatherphoto)
	#weathericon.image = weatherphoto # keep a reference!
	#imgcanvas = Canvas(weatherfr, bg="green", width=200, height=200)
	#imgcanvas.pack(side='left')

	#photoimg = tk.PhotoImage(file="default.png")
	#imgcanvas.create_image(150, 150, image=photoimg)
	#weathercanvas.delete(weathernowimage)
	#time.sleep(2)
	global weatherimgsrcb
	global weatherimgphotob
	weatherimgsrcb = Image.open("icon_weather.png")
	weatherimgphotob = ImageTk.PhotoImage(weatherimgsrcb)
	#del weathernowimage
	#weathernowimage = weathercanvas.create_image(30, 30, image=weatherimgphoto)
	weathercanvas.itemconfig(weathernowimage, image=weatherimgphotob)
	weathercanvas.itemconfig(weatherlabel, text='Weather (' + str(mylist[3]) + ') : '+"\n"+ str(mylist[0])+" : : "+ str(mylist[1]) + " °c")
	weathercanvas.itemconfig(weathersuntimes, text=str(mylist[2]))



def fnGetDlnaStatus():
	try:
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
	try:
		response = os.system('ping -c 1 -w1 wp8_tristancole')
		if response == 0:
			#yes in
			bCloser.config(fg='green')
		else:
			bCloser.config(fg='red')
	except:
		bCloser.config(fg='blue')


def fnUpdateColor():
	tick_time2 = time.strftime('%H:%M:%S')
	updatemin=tick_time2.split(':')
	if (int(updatemin[0])>=23 or int(updatemin[0])<=7):
		clock.config(fg='#491d25')
		clockdate.config(fg='#3a171d')
		weathercanvas.itemconfig(weatherlabel, fill='#444444')
		weathercanvas.itemconfig(weathersuntimes, fill='#444444')
		infodlna.config(fg='#000066')
	else:
		clock.config(fg='green')
		clockdate.config(fg='#ff6666')
		weathercanvas.itemconfig(weatherlabel, fill='white')
		weathercanvas.itemconfig(weathersuntimes, fill='yellow')
		infodlna.config(fg='blue')
		fnSetRPIbrightness(255)
		
	if (int(updatemin[0])>=23 or int(updatemin[0])<=7):
		fnSetRPIbrightness(40)
	elif (int(updatemin[0])>=22 or int(updatemin[0])<=8):
		fnSetRPIbrightness(100)



def fnSetRPIbrightness(value):
	try:
		rpibrightness = open('/sys/class/backlight/rpi_backlight/brightness', 'w')
		rpibrightness.write(str(value))
		rpibrightness.close()
	except:
		print 'fnSetRPIbrightness failed'


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
weathersuntimes = weathercanvas.create_text(700,30, font=('times',14), fill='yellow', justify='right', text='sun light')

infodlna=tk.Label(root,font=('times', 20), fg='blue',bg='black')

clock.pack(fill='both', expand=1)
clockdate.pack(fill='both', expand=1)
weathercanvas.pack(fill='both')
#weatherfr.pack(fill='both', expand=1)
infodlna.pack(fill='both',expand=1)
blnflag = True

infodlna.config(text=fnGetDlnaText())

tick()
clockdate.after(2000, fnUpdateColor)
weathercanvas.after(5000, fnGetWeather)
root.mainloop()

