# rpi_dashboard
# =================
# Night Screen Display
# - NightScreen: A simple clock and date display, with optional Z-Wave menu button

import time
import tkinter as tk
from disp.zwavefuncs import disp_zwavefuncs


class NightScreen:
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
        """ Show Display: Night Mode """
        # print("Show Night Display")

        # Display Close Button
        if self.cmdCloseNow is not None:
            bCloser = tk.Button(self.root, text='X', pady=4, padx=4, fg='red', bg='black', activeforeground='white', activebackground='black', command=self.cmdCloseNow)
            bCloser.pack(side='right')
            self.root.bind('<Escape>', self.cmdCloseNow)

        # Display Clock and Date
        self.__clock = tk.Label(self.root, font=('times', 150, 'bold'), fg='#491d25',bg='black', text=time.strftime('%H:%M:%S'))
        self.__clockdate = tk.Label(self.root, font=('times', 54, 'bold'), fg='#3a171d', bg='black', text=time.strftime('%A %d %b %Y'))
        self.__clock.pack(fill='both', expand=1)
        self.__clockdate.pack(fill='both', expand=1)

        # Display Z Menu Button
        if self.DISP_CONFIG["zwave"]["enabled"]:
            if self.zfuncs is None:
                self.zfuncs = disp_zwavefuncs(self.root, self.DISP_CONFIG["zwave"]["username"], self.DISP_CONFIG["zwave"]["password"], self.DISP_CONFIG["zwave"]["url"], self.DISP_CONFIG["zwave"]["tag"])
            self.zfuncs.addButton(0, self.DISP_CONFIG["zwave"]['night'])

        # Clock Loop
        self.__clock.after(200, self.__clockUpdate)


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
            print("ERROR:eDisplay.NightScreen.__clockUpdate()", ex)
            return 'Call updaing clock, try again'
