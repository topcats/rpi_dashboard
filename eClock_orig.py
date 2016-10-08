# -*- coding: utf-8 -*-
''' eClock.py
Use Tkinter to show a digital clock, Current weather situation and Status of TFL Line or underground line in London
Author : Atul N Yadav ( I am not complete author of this program, mostly learn from goggling the program from other programmers)
I give credit of this program to those programmers who had shared their program openly.
@https://www.facebook.com/HerambMakerLab/
v1.1 : Commented TFL status update and added UK Hot Deals Update
'''
import urllib2
import json
from string import capitalize
import time
try:
	# Python2
	import Tkinter as tk
except ImportError:
	# Python3
	import tkinter as tk

def tick(time1=''):
		try:
				global blnflag
				# get the current local time from the PC
				time2 = time.strftime('%H:%M:%S')
				# if time string has changed, update it
				if time2 != time1:
						time1 = time2
						clock.config(text=time2)
				# calls itself every 200 milliseconds
				# to update the time display as needed
				min2=time2.split(':')
				#print blnflag
				if (min2[1]=='30'or min2[1]=='00') and blnflag==True:
						mylist= fnGetWeather()
						#local_encoding = 'cp850'
						#deg = u'\xb0'.encode(local_encoding)
						#sub= "°C.".decode('utf8').encode(local_encoding)
						weather.config(text='Weather now : '+"\n"+ str(mylist[0])+" : : "+ str(mylist[1]) + " °c")	
						time.sleep(5)
						#mytfl = fnGetTflStatus()
						#tfl.config(text='TFL Status: '+"\n"+ mytfl)	
						#time.sleep(5)
						mydeal= fnGetUKDeals()
						deals.config(text='Hot Deals :' + '\n'+ mydeal)
						time.sleep(5)
						blnflag = False
				elif min2[1]!='30' and min2[1]!='00':
						blnflag = True
				clock.after(200, tick)
		except:
				print 'Error'
				return 'Call updaing clock, try again'
				tick()

def fnGetWeather():
		try: 
				url_to_call = 'http://api.openweathermap.org/data/2.5/weather?id=<location id here>&appid=<app id here>&units=metric'
				response = urllib2.urlopen(url_to_call)
				json_obj = json.load(response)
				#print url_to_call
				#print json_obj

				current_desc = capitalize(json_obj['weather'][0]['description'])
				#current_temp = kelvinToCelsius(json_obj['main']['temp'])
				current_temp = json_obj['main']['temp']

				#print current_desc
				#print current_temp
				return current_desc,current_temp
		except:
				print 'Error'
				return 'Error','Error'
	
def fnGetTflStatus():
		try:
				
				
				url_to_call='https://api.tfl.gov.uk/StopPoint/<Station_ID_here>/Disruption?getFamily=False&includeRouteBlockedStops=False&app_id=<app_id_here>&app_key=<app_key_here>
				response = urllib2.urlopen(url_to_call)
				json_obj = json.load(response)
				current_desc = capitalize(json_obj[0]['description'])
				print current_desc
				if str(current_desc)=='[]':
						status = 'Service is Good'
				else:
						status = str(current_desc)
				#print url_to_call
				#print json_obj
				return status
		except:
				print 'Error'
				return 'Call to API failed, try again'
				


def fnGetUKDeals():
		
		try:
				# To get latest clothing deals specially shirts
				url_to_call='http://api.hotukdeals.com/rest_api/v2/?key=xxxxxxxxxxxxxxxxx&order=hot&forum=deals&category=fashion&tag=shirt&shirts&trousers&output=json&results_per_page=5'
				response = urllib2.urlopen(url_to_call)
				json_obj = json.load(response)
				current_desc_1 = capitalize(json_obj['deals']['items'][0]['title'])
				status = current_desc_1
				# To get latest Perfume deals
				url_to_call='http://api.hotukdeals.com/rest_api/v2/?key=xxxxxxxxxxxxxxxxxx&order=hot&forum=deals&category=fashion&tag=perfume&output=json&results_per_page=5'
				
				response = urllib2.urlopen(url_to_call)
				json_obj = json.load(response)
				current_desc_1 = capitalize(json_obj['deals']['items'][0]['title'])
				status = status + '\n' + current_desc_1
				
				print status
				if status =='':
						status = 'No Hot Deals Mate'
				#print url_to_call
				#print json_obj
				return status
		except:
				print 'Error'
				return 'Call to API failed, try again'
root = tk.Tk()
root.attributes("-fullscreen",True)
clock = tk.Label(root, font=('times', 50, 'bold'), fg='green',bg='black')
weather=tk.Label(root,font=('times', 30), fg='white',bg='black')
#tfl=tk.Label(root,font=('times', 30), fg='white',bg='black')
deals=tk.Label(root,font=('times', 20), fg='white',bg='black',wraplength=500)
clock.pack(fill='both', expand=1)
weather.pack(fill='both', expand=1)
#tfl.pack(fill='both',expand=1)
deals.pack(fill='both',expand=1)
blnflag = True
tick()
root.mainloop()
