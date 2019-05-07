# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
from string import capitalize
from PIL import Image, ImageTk
from Crypto.Cipher import AES
from zWaveApi import *
import time
import datetime
import os
import ConfigParser
try:
    # Python2
    import Tkinter as tk
    from Tkinter import Frame, Canvas
except ImportError:
    # Python3
    import tkinter as tk
    from tkinter import Frame, Canvas

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


def tick(tick_time1=''):
    try:
        global blnflag
        # get the current local time from the PC
        tick_time2 = time.strftime('%H:%M:%S')
        # if time string has changed, update it
        if tick_time2 != tick_time1:
            tick_time1 = tick_time2
            clock.config(text=tick_time2)
            fnGetOwnerHome()
        # calls itself every 200 milliseconds
        # to update the time display as needed
        min2=tick_time2.split(':')
        if (min2[1]=='31' or min2[1]=='01') and blnflag==True:
            #Update Date and set colours
            clockdate.config(text=time.strftime('%A %d %b %Y'))
            fnUpdateColor()
            fnGetWeather()
            infodlna.config(text=fnGetDlnaText())

            blnflag = False
        elif min2[1]!='31' and min2[1]!='01':
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
        with open('data_forcast.txt') as fp:
            json_objb = json.load(fp)

        current_desc = capitalize(json_obj['weather'][0]['description'])
        #current_temp = kelvinToCelsius(json_obj['main']['temp'])
        current_temp = json_obj['main']['temp']
        current_time = datetime.datetime.fromtimestamp(int(json_obj['dt'])).strftime('%H:%M')
        current_location = json_obj['name']
        current_sunlight = datetime.datetime.fromtimestamp(int(json_obj['sys']['sunrise'])).strftime('%H:%M')
        current_sunlight = current_sunlight + ' - '
        current_sunlight = current_sunlight + datetime.datetime.fromtimestamp(int(json_obj['sys']['sunset'])).strftime('%H:%M')
        #forcast_times = '00:00        01:00        02:00        03:00        04:00'
        
        forcast_times = datetime.datetime.fromtimestamp(int(json_objb['list'][0]['dt'])).strftime('%H:%M')
        forcast_times = forcast_times + '        '
        forcast_times = forcast_times + datetime.datetime.fromtimestamp(int(json_objb['list'][1]['dt'])).strftime('%H:%M')
        forcast_times = forcast_times + '        '
        forcast_times = forcast_times + datetime.datetime.fromtimestamp(int(json_objb['list'][2]['dt'])).strftime('%H:%M')
        forcast_times = forcast_times + '        '
        forcast_times = forcast_times + datetime.datetime.fromtimestamp(int(json_objb['list'][3]['dt'])).strftime('%H:%M')
        forcast_times = forcast_times + '       '
        forcast_times = forcast_times + datetime.datetime.fromtimestamp(int(json_objb['list'][4]['dt'])).strftime('%H:%M')
        forcast_times = forcast_times + ' '

        return current_desc,current_temp,current_sunlight,current_location,current_time,forcast_times
    
    except:
        print 'Error:fnGetWeather'
        return 'Error','Error','00:00 - 00:00','unknown', '00:00', '00:00'


def fnGetWeather():
    # update weather text
    mylist = fnGetWeatherStatus()
    weathercanvas.itemconfig(weatherlabel, text='Weather (' + str(mylist[3]) + ') : '+"\n"+ str(mylist[0])+" : : "+ str(mylist[1]) + " °c")
    weathercanvas.itemconfig(weathersuntimes, text=str(mylist[2]))
    weathercanvas.itemconfig(weathernowtime, text=str(mylist[4]))
    weathercanvas.itemconfig(weatherforetext, text=str(mylist[5]))
    
    
    # Update weather icons
    global weatherimgsrcb
    global weatherimgphotob
    global weatherimgsrcf1
    global weatherimgphotof1
    global weatherimgsrcf2
    global weatherimgphotof2
    global weatherimgsrcf3
    global weatherimgphotof3
    global weatherimgsrcf4
    global weatherimgphotof4
    global weatherimgsrcf5
    global weatherimgphotof5
    
    try:
        if os.path.isfile ('icon_weather.png'): 
            weatherimgsrcb = Image.open("icon_weather.png")
            weatherimgphotob = ImageTk.PhotoImage(weatherimgsrcb)
            weathercanvas.itemconfig(weathernowimage, image=weatherimgphotob)
        if os.path.isfile ('icon_forcast1.png'): 
            weatherimgsrcf1 = Image.open("icon_forcast1.png")
            weatherimgphotof1 = ImageTk.PhotoImage(weatherimgsrcf1)
            weathercanvas.itemconfig(weatherfore1image, image=weatherimgphotof1)
        if os.path.isfile ('icon_forcast2.png'): 
            weatherimgsrcf2 = Image.open("icon_forcast2.png")
            weatherimgphotof2 = ImageTk.PhotoImage(weatherimgsrcf2)
            weathercanvas.itemconfig(weatherfore2image, image=weatherimgphotof2)
        if os.path.isfile ('icon_forcast3.png'): 
            weatherimgsrcf3 = Image.open("icon_forcast3.png")
            weatherimgphotof3 = ImageTk.PhotoImage(weatherimgsrcf3)
            weathercanvas.itemconfig(weatherfore3image, image=weatherimgphotof3)
        if os.path.isfile ('icon_forcast4.png'): 
            weatherimgsrcf4 = Image.open("icon_forcast4.png")
            weatherimgphotof4 = ImageTk.PhotoImage(weatherimgsrcf4)
            weathercanvas.itemconfig(weatherfore4image, image=weatherimgphotof4)
        if os.path.isfile ('icon_forcast5.png'): 
            weatherimgsrcf5 = Image.open("icon_forcast5.png")
            weatherimgphotof5 = ImageTk.PhotoImage(weatherimgsrcf5)
            weathercanvas.itemconfig(weatherfore5image, image=weatherimgphotof5)
    except:
        print 'some weather icon update error'



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
    if int(config.get('DLNA', 'Refresh')) == 0:
        return ''
    else:
        mydlna = fnGetDlnaStatus()
        return 'DLNA Status: '+"\n"+ 'VID:'+mydlna[0]+'  MP3:'+mydlna[1]


def fnGetOwnerHome():
    try:
        response = os.system('ping -c 1 -w1 '+config.get('Owner','PhoneIP')+' > /dev/null 2>&1')
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
        weathercanvas.itemconfig(weatherforetext, fill='#444444')
        weathercanvas.itemconfig(weathernowtime, fill='#444444')
        infodlna.config(fg='#000066')
    else:
        clock.config(fg='green')
        clockdate.config(fg='#ff6666')
        weathercanvas.itemconfig(weatherlabel, fill='white')
        weathercanvas.itemconfig(weathersuntimes, fill='yellow')
        weathercanvas.itemconfig(weatherforetext, fill='white')
        weathercanvas.itemconfig(weathernowtime, fill='white')
        infodlna.config(fg='blue')
        fnSetRPIbrightness(255)
        
    if (int(updatemin[0])<=6):
        fnSetRPIbrightness(20)
    elif (int(updatemin[0])>=23 or int(updatemin[0])<=7):
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


def cmdCloseNow():
    print 'Closing now...'
    root.destroy()
    time.sleep(1)
    #sys.exit()


def cmdShowZwaveMenu():
    global zwavecanvas
    global tk
    global zwaveopen
    mypihostname = socket.gethostname().zfill(16)
    mypiserial = getserial().zfill(16)
    cipherobj = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    zwavecanvas = Canvas(root, bg='blue', borderwidth=2)
    zwavecanvas.place(x=(root.winfo_screenwidth()-230), y=(root.winfo_screenheight()-200))
    oZWave = zWaveApi(config.get('ZWave', 'username'), cipherobj.decrypt(config.get('ZWave', 'password')), config.get('ZWave', 'url'))
    oZDevices = oZWave.getDevices()

    for zDeviceItem in oZDevices:
        if (zDeviceItem['tags'].count('ShowDashboard') >0):
            if (zDeviceItem['deviceType'] == 'toggleButton'):
                zwavecmdtb = tk.Button(zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', width=20, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : cmdActionZwave(p1, p2))
                zwavecmdtb.pack()
            elif (zDeviceItem['deviceType'] == 'switchBinary'):
                if (zDeviceItem['metrics']['level'] == 'on'):
                    zwavecmdsb = tk.Button(zwavecanvas, text=zDeviceItem['metrics']["title"], fg='red', width=20, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'off' : cmdActionZwave(p1, p2))
                    zwavecmdsb.pack()
                else:
                    zwavecmd = tk.Button(zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', width=20, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : cmdActionZwave(p1, p2))
                    zwavecmd.pack()
            elif (zDeviceItem['deviceType'] == 'switchMultilevel'):
                if (int(zDeviceItem['metrics']['level']) == 0):
                    zwavecmd = tk.Button(zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', width=20, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : cmdActionZwave(p1, p2))
                    zwavecmd.pack()
                else:
                    zwavecmd = tk.Button(zwavecanvas, text=zDeviceItem['metrics']["title"], fg='red', width=20, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'off' : cmdActionZwave(p1, p2))
                    zwavecmd.pack()
    cx = (zwaveopen.winfo_rootx() + zwaveopen.winfo_reqwidth()) - (zwavecanvas.winfo_reqwidth()/2)
    cy = (zwaveopen.winfo_rooty() + zwaveopen.winfo_reqheight()) - (zwavecanvas.winfo_reqheight()/2)
    zwavecanvas.place(x=cx, y=cy)
    zwavecanvas.after(10000, cmdHideZwaveMenu)


def cmdHideZwaveMenu():
    global zwavecanvas
    zwavecanvas.delete("all")
    zwavecanvas.place_forget()

def cmdActionZwave(zID, zAction):
    mypihostname = socket.gethostname().zfill(16)
    mypiserial = getserial().zfill(16)
    cipherobj = AES.new(mypihostname, AES.MODE_CFB, mypiserial)
    oZWave = zWaveApi(config.get('ZWave', 'username'), cipherobj.decrypt(config.get('ZWave', 'password')), config.get('ZWave', 'url'))
    oZWave.setDeviceCommand(zID, zAction)
    cmdHideZwaveMenu()

####################################################
#main program
root = tk.Tk()
root.attributes("-fullscreen",True)
root.config(cursor="none")
root.config(background="black")

# Display Close Button
bCloser = tk.Button(root, text='X', fg='red', bg='black', command=cmdCloseNow)
bCloser.pack(side='right')
root.bind('<Escape>', cmdCloseNow)

# Display Clock and Date 
clock = tk.Label(root, font=('times', 50, 'bold'), fg='green',bg='black')
clockdate = tk.Label(root, font=('times', 30, 'bold'), fg='#ff6666', bg='black', text=time.strftime('%A %d %b %Y'))

# Display Weather info
weathercanvas = Canvas(root, bg="black", width=700, height=170, borderwidth=0)
weatherimgsrc = Image.open("default.png")
weatherimgphoto = ImageTk.PhotoImage(weatherimgsrc)
weathernowimage = weathercanvas.create_image(30, 30, image=weatherimgphoto)
weatherlabel = weathercanvas.create_text(300, 46, font=('times', 26), fill='white', justify='center', text='Weather Info')
weathernowtime = weathercanvas.create_text(30, 60, font=('times',14), fill='white', justify='center', text='00:00')
weathersuntimes = weathercanvas.create_text(700, 30, font=('times',14), fill='yellow', justify='right', text='sun light')
weatherfore1image = weathercanvas.create_image(120, 120, image=weatherimgphoto)
weatherfore2image = weathercanvas.create_image(200, 120, image=weatherimgphoto)
weatherfore3image = weathercanvas.create_image(280, 120, image=weatherimgphoto)
weatherfore4image = weathercanvas.create_image(360, 120, image=weatherimgphoto)
weatherfore5image = weathercanvas.create_image(440, 120, image=weatherimgphoto)
weatherforetext = weathercanvas.create_text(280, 150, font=('times',14), fill='white', justify='center', text='00:00')

# Display DLNA info
infodlna=tk.Label(root,font=('times', 20), fg='blue',bg='black')


# Display z-wave Menu
if int(config.get('ZWave', 'enabled')) == 1:
    zwaveopen=tk.Button(root, text='Z', font=('Helvetica', 14, 'bold'), fg='white', bg='blue', highlightbackground='blue', highlightcolor='white', command=cmdShowZwaveMenu)
    zwaveopen.place(x=(root.winfo_screenwidth()-50), y=(root.winfo_screenheight()-50), width=30, height=30)


# Display info on screen
clock.pack(fill='both', expand=1)
clockdate.pack(fill='both', expand=1)
weathercanvas.pack(fill='both')
infodlna.pack(fill='both',expand=1)
blnflag = True

infodlna.config(text=fnGetDlnaText())

tick()
clockdate.after(2000, fnUpdateColor)
weathercanvas.after(5000, fnGetWeather)
root.mainloop()

