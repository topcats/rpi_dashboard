# rpi_dashboard
# =================
# Day Screen Display
# - DayScreen: A clock and date display, with weather information, with optional Z-Wave menu button

import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from disp.weatherfuncs import disp_weatherfuncs
from disp.zwavefuncs import disp_zwavefuncs


class DayScreen:

    __weathercanvas = None
    __weatherimgsrc = None
    __weatherimgphoto = None
    __weathernowimage = None
    __weatherimgsrcb = None
    __weatherlabel = None
    __weathernowtime = None
    __weathersuntimes = None
    __weatherfore1image = None
    __weatherfore2image = None
    __weatherfore3image = None
    __weatherfore4image = None
    __weatherfore5image = None
    __weatherforetext = None
    __weatherimgphotob = None
    __weatherimgsrcf1 = None
    __weatherimgsrcf2 = None
    __weatherimgsrcf3 = None
    __weatherimgsrcf4 = None
    __weatherimgsrcf5 = None
    __weatherimgphotof1 = None
    __weatherimgphotof2 = None
    __weatherimgphotof3 = None
    __weatherimgphotof4 = None
    __weatherimgphotof5 = None

    def __init__(self, tkroot,
                 disp_config,
                 closefunc=None):
        
        # init system
        self.root = tkroot
        self.DISP_CONFIG = disp_config
        self.cmdCloseNow = closefunc

        self.__clock = None
        self.__clockdate = None
        self.zfuncs = None
        self.__blnflag = True


    def showDisplay(self):
        """ Show Display: Day Mode """
        # print("Show Day Display")

        # Display Close Button
        if self.cmdCloseNow is not None:
            bCloser = tk.Button(self.root, text='X', pady=4, padx=4, fg='red', bg='black', activeforeground='white', activebackground='black', command=self.cmdCloseNow)
            bCloser.pack(side='right')
            self.root.bind('<Escape>', self.cmdCloseNow)

        # Display Clock and Date
        self.__clock = tk.Label(self.root, font=('times', 120, 'bold'), fg='green',bg='black', text=time.strftime('%H:%M:%S'))
        self.__clockdate = tk.Label(self.root, font=('times', 40, 'bold'), fg='#ff6666', bg='black', text=time.strftime('%A %d %b %Y'))
        self.__clock.pack(fill='both', expand=1)
        self.__clockdate.pack(fill='both', expand=1)

        # Display Weather info
        self.__weathercanvas = tk.Canvas(self.root, bg="black", width=700, height=176, borderwidth=0)
        self.__weathercanvas.hidden = 0
        self.__weatherimgsrc = Image.open("data/weather/default.png")
        self.__weatherimgphoto = ImageTk.PhotoImage(self.__weatherimgsrc)
        self.__weathernowimage = self.__weathercanvas.create_image(60, 60, image=self.__weatherimgphoto)
        self.__weatherlabel = self.__weathercanvas.create_text(320, 46, font=('times', 26), fill='white', justify='left', text='Weather Info')
        self.__weathernowtime = self.__weathercanvas.create_text(60, 120, font=('times',16), fill='white', justify='center', text='00:00')
        self.__weathersuntimes = self.__weathercanvas.create_text(660, 30, font=('times',20), fill='yellow', justify='right', text='sun light')
        self.__weatherfore1image = self.__weathercanvas.create_image(170, 120, image=self.__weatherimgphoto)
        self.__weatherfore2image = self.__weathercanvas.create_image(260, 120, image=self.__weatherimgphoto)
        self.__weatherfore3image = self.__weathercanvas.create_image(350, 120, image=self.__weatherimgphoto)
        self.__weatherfore4image = self.__weathercanvas.create_image(440, 120, image=self.__weatherimgphoto)
        self.__weatherfore5image = self.__weathercanvas.create_image(530, 120, image=self.__weatherimgphoto)
        self.__weatherforetext = self.__weathercanvas.create_text(350, 160, font=('times',14), fill='white', justify='center', text='00:00')
        self.__weathercanvas.pack(fill='both')

        # Display Z Menu Button
        if self.DISP_CONFIG["zwave"]["enabled"]:
            if self.zfuncs is None:
                self.zfuncs = disp_zwavefuncs(self.root, self.DISP_CONFIG["zwave"]["username"], self.DISP_CONFIG["zwave"]["password"], self.DISP_CONFIG["zwave"]["url"], self.DISP_CONFIG["zwave"]["tag"])
            self.zfuncs.addButton(1, self.DISP_CONFIG["zwave"]['day'])

        # Clock Loop
        self.__clock.after(200, self.__clockUpdate)
        self.__weathercanvas.after(500, self.__weatherUpdate)


    def __clockUpdate(self, tick_time1=''):
        """
        Update the Clock Display every second.

        Update the Date Display every 30 minutes.
        """
        try:
            # get the current local time from the PC
            tick_time2 = time.strftime('%H:%M:%S')
            # if time string has changed, update it
            if tick_time2 != tick_time1:
                tick_time1 = tick_time2
                self.__clock.config(text=tick_time2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            min2=tick_time2.split(':')
            if (min2[1]=='31' or min2[1]=='01') and self.__blnflag==True:
                #Update Date
                self.__clockdate.config(text=time.strftime('%A %d %b %Y'))
                self.__blnflag = False
            elif min2[1]!='31' and min2[1]!='01':
                self.__blnflag = True

            self.__clock.after(200, self.__clockUpdate)
        except Exception as ex:
            print("ERROR:eDisplay.DayScreen.__clockUpdate()", ex)
            return 'Call updaing clock, try again'


    def __weatherUpdate(self):
        """ Update the Weather Display every 10 minutes. """
        try:
            # Get Weather Data
            datapath = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/weather'))
            weatherfunc = disp_weatherfuncs(datapath, self.DISP_CONFIG["weather"])
            weathercurrent = weatherfunc.GetCurrent()
            weatherforecast = weatherfunc.GetForecast()

            # update weather text
            self.__weathercanvas.itemconfig(self.__weatherlabel, text='Weather (' + str(weathercurrent['location']) + ') : '+"\n"+ str(weathercurrent['description'])+" : : "+ str(weathercurrent['temperature']) + " c")
            self.__weathercanvas.itemconfig(self.__weathersuntimes, text=str(weathercurrent['sunlight']))
            self.__weathercanvas.itemconfig(self.__weathernowtime, text=str(weathercurrent['time']))

            # update forecast text
            # forcast_times = '00:00        01:00        02:00        03:00        04:00'
            forcast_times = ''
            forcast_times = forcast_times + weatherforecast[0]['time']
            forcast_times = forcast_times + '          '
            forcast_times = forcast_times + weatherforecast[1]['time']
            forcast_times = forcast_times + '          '
            forcast_times = forcast_times + weatherforecast[2]['time']
            forcast_times = forcast_times + '          '
            forcast_times = forcast_times + weatherforecast[3]['time']
            forcast_times = forcast_times + '          '
            forcast_times = forcast_times + weatherforecast[4]['time']
            forcast_times = forcast_times + ' '
            self.__weathercanvas.itemconfig(self.__weatherforetext, text=str(forcast_times))

            # update weather images
            if os.path.isfile ('data/weather/icon_'+str(weathercurrent['icon'])+'.png'):
                self.__weatherimgsrcb = Image.open('data/weather/icon_'+str(weathercurrent['icon'])+'.png')
                self.__weatherimgsrcb = self.__weatherimgsrcb.resize((140,140))
                self.__weatherimgphotob = ImageTk.PhotoImage(self.__weatherimgsrcb)
                self.__weathercanvas.itemconfig(self.__weathernowimage, image=self.__weatherimgphotob)
            if os.path.isfile ('data/weather/icon_'+str(weatherforecast[0]['icon'])+'.png'):
                self.__weatherimgsrcf1 = Image.open('data/weather/icon_'+str(weatherforecast[0]['icon'])+'.png')
                self.__weatherimgphotof1 = ImageTk.PhotoImage(self.__weatherimgsrcf1)
                self.__weathercanvas.itemconfig(self.__weatherfore1image, image=self.__weatherimgphotof1)
            if os.path.isfile ('data/weather/icon_'+str(weatherforecast[1]['icon'])+'.png'):
                self.__weatherimgsrcf2 = Image.open('data/weather/icon_'+str(weatherforecast[1]['icon'])+'.png')
                self.__weatherimgphotof2 = ImageTk.PhotoImage(self.__weatherimgsrcf2)
                self.__weathercanvas.itemconfig(self.__weatherfore2image, image=self.__weatherimgphotof2)
            if os.path.isfile ('data/weather/icon_'+str(weatherforecast[2]['icon'])+'.png'):
                self.__weatherimgsrcf3 = Image.open('data/weather/icon_'+str(weatherforecast[2]['icon'])+'.png')
                self.__weatherimgphotof3 = ImageTk.PhotoImage(self.__weatherimgsrcf3)
                self.__weathercanvas.itemconfig(self.__weatherfore3image, image=self.__weatherimgphotof3)
            if os.path.isfile ('data/weather/icon_'+str(weatherforecast[3]['icon'])+'.png'):
                self.__weatherimgsrcf4 = Image.open('data/weather/icon_'+str(weatherforecast[3]['icon'])+'.png')
                self.__weatherimgphotof4 = ImageTk.PhotoImage(self.__weatherimgsrcf4)
                self.__weathercanvas.itemconfig(self.__weatherfore4image, image=self.__weatherimgphotof4)
            if os.path.isfile ('data/weather/icon_'+str(weatherforecast[4]['icon'])+'.png'):
                self.__weatherimgsrcf5 = Image.open('data/weather/icon_'+str(weatherforecast[4]['icon'])+'.png')
                self.__weatherimgphotof5 = ImageTk.PhotoImage(self.__weatherimgsrcf5)
                self.__weathercanvas.itemconfig(self.__weatherfore5image, image=self.__weatherimgphotof5)

        except Exception as ex:
            print("ERROR:eDisplay.DayScreen.__weatherUpdate()", ex)

        # schedule next update in 10 minutes
        self.__weathercanvas.after(600000, self.__weatherUpdate)
