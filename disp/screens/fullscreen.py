# rpi_dashboard
# =================
# Full Display Screen
# - Home Screen: Weather now, Calendar
# - Weather Screen: Weather and Forecast
# - House Screen: House Control

from email.mime import image
import os
import time
import tkinter as tk
from PIL import Image, ImageTk
from disp.screens.ui.blockbutton import *
from disp.screens.ui.blockitem import *
from disp.screens.ui import colours
from disp.calendarfuncs import *
from disp.menufuncs import *
from disp.weatherfuncs import disp_weatherfuncs
from disp.zwavefuncs import disp_zwavefuncs


class FullScreen:

    root = None
    DISP_CONFIG = None
    cmdCloseNow = None
    zfuncs = None
    bgcanvas = None
    __maincanvas = None
    __maincanvasafterid = None
    __subcanvas = None
    __subcanvasafterid = None
    __bgcanvasimgsrc = None
    __bgcanvasimgphoto = None
    __bgcanvasimage = None
    __weatherimgsrc = None
    __weatherimgphoto = None
    __weathernowimage = None
    __weatherimgsrcf1 = None
    __weatherimgsrcf2 = None
    __weatherimgsrcf3 = None
    __weatherimgsrcf4 = None
    __weatherimgphotof1 = None
    __weatherimgphotof2 = None
    __weatherimgphotof3 = None
    __weatherimgphotof4 = None
    __weatherfore1image = None
    __weatherfore2image = None
    __weatherfore3image = None
    __weatherfore4image = None

    def __init__(self, tkroot,
                 disp_config,
                 closefunc=None):

        # init system
        self.root = tkroot
        self.DISP_CONFIG = disp_config
        self.cmdCloseNow = closefunc

        # setup paths
        self.__datapathweat = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/weather"))
        self.__datapathcal = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/calendar"))
        self.__datapathmenu = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../data/menu"))


    def showDisplay(self):
        """ Show Display: Full Mode """
        # printS("Show Full Display")

        # Map Close Button
        if self.cmdCloseNow is not None:
            self.root.bind('<Escape>', self.cmdCloseNow)

        # apply background image
        if self.bgcanvas is None:
            self.bgcanvas = tk.Canvas(self.root, bg=colours.LCARS_BG, width=800, height=480, borderwidth=0, highlightthickness=0)
            self.bgcanvas.hidden = 0
            self.__bgcanvasimgsrc = Image.open("disp/screens/assets/lcars_screen_1.png")
            self.__bgcanvasimgphoto = ImageTk.PhotoImage(self.__bgcanvasimgsrc)
            self.__bgcanvasimage = self.bgcanvas.create_image(0, 0, image=self.__bgcanvasimgphoto, anchor="nw")
            self.bgcanvas.image = self.__bgcanvasimgphoto
            self.bgcanvas.place(x=0, y=0, width=800, height=480)

        # Set Header and Date/Time
        LcarsText(self.root, colours.ORANGE, (150, 0), "TheOwls - 2HP", size=1.7)
        LcarsText(self.root, colours.BLUE, (680, 4), "", size=1.5).isClock()
        LcarsText(self.root, colours.BLACK, (462, 444), "", size=0.78, bg_colour=colours.BLUEGREY).isDate()

        # Set left menu buttons
        LcarsBlockMedium(self.root, colours.MAUVE, (16, 145), "HOME", handler=self.__showHome )
        LcarsBlockSmall(self.root, colours.ORANGE, (16, 211), "WEATHER", handler=self.__showWeather )
        if self.DISP_CONFIG["zwave"]["enabled"]:
            LcarsBlockLarge(self.root, colours.PEACH, (16, 249), "HOUSE", handler=self.__showHouse )

        # Show inital screen
        self.__showHome()


        # # Display Close Button
        # if self.cmdCloseNow is not None:
        #     bCloser = tk.Button(self.root, text="X', pady=4, padx=4, fg='red', bg='black', activeforeground='white', activebackground='black', command=self.cmdCloseNow)
        #     bCloser.pack(side='right')
        #     self.root.bind('<Escape>', self.cmdCloseNow)



        # Display Z Menu Button
        if self.DISP_CONFIG["zwave"]["enabled"]:
            if self.zfuncs is None:
                self.zfuncs = disp_zwavefuncs(self.root, self.DISP_CONFIG["zwave"]["username"], self.DISP_CONFIG["zwave"]["password"], self.DISP_CONFIG["zwave"]["url"], self.DISP_CONFIG["zwave"]["tag"])


    def __showHome(self):
        """
        Show the General information pane
        """

        # Clear and setup canvas
        self.__clearMainCanvas()

        # Refresh every 5 minutes
        self.__maincanvasafterid = self.__maincanvas.after(300000, self.__showHome)

        #Front Page Weather
        try:
            # Get Weather Data
            weatherfunc = disp_weatherfuncs(self.__datapathweat, self.DISP_CONFIG["weather"])
            weathercurrent = weatherfunc.GetCurrent()

            # Show Current Weather
            LcarsText(self.__maincanvas, colours.VIOLET, (10, 150), str(weathercurrent["time"]), size=1.2)
            LcarsText(self.__maincanvas, colours.BLUE, (10, 190), str(weathercurrent["temperature"])+ " c", size=1.2)
            LcarsText(self.__maincanvas, colours.BLUE, (10, 225), str(weathercurrent["description"]) + "\n" + str(weathercurrent["wind"]), size=1.2)
            if os.path.isfile ("data/weather/icon_"+str(weathercurrent["icon"])+".png"):
                self.__weatherimgsrc = Image.open("data/weather/icon_"+str(weathercurrent["icon"])+".png")
                self.__weatherimgsrc = self.__weatherimgsrc.resize((150,150))
                self.__weatherimgphoto = ImageTk.PhotoImage(self.__weatherimgsrc)
                self.__weathernowimage = self.__maincanvas.create_image(140, 170, image=self.__weatherimgphoto)
                self.__maincanvas.image = self.__weatherimgphoto
        except Exception as ex:
            print("ERROR:eDisplay.FullScreen.__showHome(Weather)", ex)

        # Front Page Calendar
        calendarTop = 40
        try:
            LcarsText(self.__maincanvas, colours.VIOLET, (300, 0), "HOUSE CALENDAR TODAY", size=1, anchor=tk.NW)
            # Get Calendar for Today
            calendarfuncs = disp_calendarfuncs(self.__datapathcal, self.DISP_CONFIG["location"])
            currentEvents = calendarfuncs.getToday()

            for o365_event in currentEvents:
                calendarColour = o365_event.GetColour()
                calendarText = o365_event.GetText()
                LcarsText(self.__maincanvas, calendarColour, (180, calendarTop), str(calendarText), size=1.2, anchor=tk.NW)
                calendarTop += 38
        except Exception as ex:
            print("ERROR:eDisplay.FullScreen.__showHome(Calendar)", ex)

        # Front Page Menu
        try:
            # Get Menu Data for Today if before 8pm else tomorrow
            currentdatetime = datetime.now()

            menufuncs = disp_menufuncs(self.__datapathmenu, self.DISP_CONFIG["location"])
            if currentdatetime.hour < 20:  # Before 8pm
                currentMenu = menufuncs.getToday()
            else:  # After 8pm, show tomorrow's menu
                currentMenu = menufuncs.getTomorrow()

            if currentMenu is not None and len(currentMenu) > 0:
                LcarsText(self.__maincanvas, colours.BLUE, (180, calendarTop), str(currentMenu[0].GetText()), size=1.2, anchor=tk.NW)

        except Exception as ex:
            print("ERROR:eDisplay.FullScreen.__showHome(Menu)", ex)


    def __showWeather(self):
        """
        Show the Weather information pane
        """

        # Clear and setup canvas
        self.__clearMainCanvas()

        # Timeout after 3 minutes
        self.__maincanvasafterid = self.__maincanvas.after(180000, self.__showHome)

        try:
            # Get Weather Data
            weatherfunc = disp_weatherfuncs(self.__datapathweat, self.DISP_CONFIG["weather"])
            weathercurrent = weatherfunc.GetCurrent()
            weatherforecast = weatherfunc.GetForecast()

            # update weather text
            LcarsText(self.__maincanvas, colours.VIOLET, (0, 0), "Weather (" + str(weathercurrent["location"]) + ")", size=2)

            # Show Current
            LcarsText(self.__maincanvas, colours.BLUE, (10, 60), str(weathercurrent["description"])+" : : "+ str(weathercurrent["temperature"]) + " c", size=1.8)
            LcarsText(self.__maincanvas, colours.BLUE, (10, 120), "Sun rise : " + str(weathercurrent["sunlight"]), size=1.2)
            LcarsText(self.__maincanvas, colours.VIOLET, (520, 120), str(weathercurrent["time"]), size=1.2, anchor=tk.CENTER)
            if os.path.isfile ("data/weather/icon_"+str(weathercurrent["icon"])+".png"):
                self.__weatherimgsrc = Image.open("data/weather/icon_"+str(weathercurrent["icon"])+".png")
                self.__weatherimgsrc = self.__weatherimgsrc.resize((180,180))
                self.__weatherimgphoto = ImageTk.PhotoImage(self.__weatherimgsrc)
                self.__weathernowimage = self.__maincanvas.create_image(536, 50, image=self.__weatherimgphoto)
                self.__maincanvas.image = self.__weatherimgphoto

            # Show Forecast
            if os.path.isfile ("data/weather/icon_"+str(weatherforecast[0]["icon"])+".png"):
                LcarsText(self.__maincanvas, colours.VIOLET, (10, 170), str(weatherforecast[0]["time"]), size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (10, 205), str(weatherforecast[0]["temperature"])+" c", size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (10, 240), str(weatherforecast[0]["description"])+"\n"+str(weatherforecast[0]["wind"]), size=1, anchor=tk.W)
                self.__weatherimgsrcf1 = Image.open("data/weather/icon_"+str(weatherforecast[0]["icon"])+".png")
                self.__weatherimgphotof1 = ImageTk.PhotoImage(self.__weatherimgsrcf1)
                self.__weatherfore1image = self.__maincanvas.create_image(105, 200, image=self.__weatherimgphotof1)
                self.__maincanvas.image = self.__weatherimgphotof1
            if os.path.isfile ("data/weather/icon_"+str(weatherforecast[1]["icon"])+".png"):
                LcarsText(self.__maincanvas, colours.VIOLET, (165, 170), str(weatherforecast[1]["time"]), size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (165, 205), str(weatherforecast[1]["temperature"])+" c", size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (165, 240), str(weatherforecast[1]["description"])+"\n"+str(weatherforecast[1]["wind"]), size=1, anchor=tk.W)
                self.__weatherimgsrcf2 = Image.open("data/weather/icon_"+str(weatherforecast[1]["icon"])+".png")
                self.__weatherimgphotof2 = ImageTk.PhotoImage(self.__weatherimgsrcf2)
                self.__weatherfore2image = self.__maincanvas.create_image(260, 200, image=self.__weatherimgphotof2)
                self.__maincanvas.image = self.__weatherimgphotof2
            if os.path.isfile ("data/weather/icon_"+str(weatherforecast[2]["icon"])+".png"):
                LcarsText(self.__maincanvas, colours.VIOLET, (320, 170), str(weatherforecast[2]["time"]), size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (320, 205), str(weatherforecast[2]["temperature"])+" c", size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (320, 240), str(weatherforecast[2]["description"])+"\n"+str(weatherforecast[2]["wind"]), size=1, anchor=tk.W)
                self.__weatherimgsrcf3 = Image.open("data/weather/icon_"+str(weatherforecast[2]["icon"])+".png")
                self.__weatherimgphotof3 = ImageTk.PhotoImage(self.__weatherimgsrcf3)
                self.__weatherfore3image = self.__maincanvas.create_image(415, 200, image=self.__weatherimgphotof3)
                self.__maincanvas.image = self.__weatherimgphotof3
            if os.path.isfile ("data/weather/icon_"+str(weatherforecast[3]["icon"])+".png"):
                LcarsText(self.__maincanvas, colours.VIOLET, (470, 170), str(weatherforecast[3]["time"]), size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (470, 205), str(weatherforecast[3]["temperature"])+" c", size=1, anchor=tk.E, width=5)
                LcarsText(self.__maincanvas, colours.BLUE, (475, 240), str(weatherforecast[3]["description"])+"\n"+str(weatherforecast[3]["wind"]), size=1, anchor=tk.W)
                self.__weatherimgsrcf4 = Image.open("data/weather/icon_"+str(weatherforecast[3]["icon"])+".png")
                self.__weatherimgphotof4 = ImageTk.PhotoImage(self.__weatherimgsrcf4)
                self.__weatherfore4image = self.__maincanvas.create_image(570, 200, image=self.__weatherimgphotof4)
                self.__maincanvas.image = self.__weatherimgphotof4

        except Exception as ex:
            print("ERROR:eDisplay.FullScreen.__showWeather()", ex)


    def __showHouse(self):
        """
        Show the House Control pane
        """

        def getSensorTemp(sensorList = []):
            if sensorList == []:
                return ""
            # Find Sensor with Temp tag
            sensorItem = [d for d in sensorList if "Temp" in d['tags'] ]
            if sensorItem is None or sensorItem == []:
                return ""
            return "{:.1f} c ".format(sensorItem[0]["metrics"]["level"])

        def getSensorLux(sensorList = []):
            if sensorList == []:
                return ""
            # Find Sensor with Temp tag
            sensorItem = [d for d in sensorList if "Lux" in d['tags'] ]
            if sensorItem is None or sensorItem == []:
                return ""
            return "{:.0f} ".format(sensorItem[0]["metrics"]["level"])

        def drawsub(room=0):
            self.__clearSubCanvas()
            if room == 0:
                return
            if self.__maincanvasafterid is not None:
                self.__maincanvas.after_cancel(self.__maincanvasafterid)
            self.__maincanvasafterid = self.__maincanvas.after(120000, self.__showHome)

            LocationName = self.zfuncs.getRoomName(room)
            roomButtons = self.zfuncs.getRoomDevices(self.DISP_CONFIG["zwave"]["full"], room)
            buttonTopSub = 30
            for zDeviceItem in roomButtons:
                deviceTitle = str(zDeviceItem['metrics']["title"]).replace(' ' + LocationName + ' ', "").strip()
                if (deviceTitle.startswith(LocationName)):
                    deviceTitle = deviceTitle[len(LocationName):].strip()
                if (deviceTitle.startswith('-') or deviceTitle.startswith(':')):
                    deviceTitle = deviceTitle[1:].strip()

                if (zDeviceItem['deviceType'] == 'toggleButton'):
                    LcarsBlockSmall(self.__subcanvas, colours.CORAL, (200, buttonTopSub), deviceTitle, width=200, handler=lambda p1 = zDeviceItem['id'], p2 = 'on', p3 = room : putAction(p3, p1, p2))
                elif (zDeviceItem['deviceType'] == 'switchBinary'):
                    if (zDeviceItem['metrics']['level'] == 'on'):
                        LcarsBlockSmall(self.__subcanvas, colours.GREEN, (200, buttonTopSub), deviceTitle, width=200, handler=lambda p1 = zDeviceItem['id'], p2 = 'off', p3 = room : putAction(p3, p1, p2))
                    else:
                        LcarsBlockSmall(self.__subcanvas, colours.RED, (200, buttonTopSub), deviceTitle, width=200, handler=lambda p1 = zDeviceItem['id'], p2 = 'on', p3 = room : putAction(p3, p1, p2))
                elif (zDeviceItem['deviceType'] == 'switchMultilevel'):
                    if (int(zDeviceItem['metrics']['level']) == 0):
                        LcarsBlockSmall(self.__subcanvas, colours.RED, (200, buttonTopSub), deviceTitle, width=200, handler=lambda p1 = zDeviceItem['id'], p2 = 'on', p3 = room : putAction(p3, p1, p2))
                    else:
                        LcarsBlockSmall(self.__subcanvas, colours.GREEN, (200, buttonTopSub), deviceTitle, width=200, handler=lambda p1 = zDeviceItem['id'], p2 = 'off', p3 = room : putAction(p3, p1, p2))
                buttonTopSub += 50

        def putAction(roomid, deviceid, deviceaction):
            if self.__maincanvasafterid is not None:
                self.__maincanvas.after_cancel(self.__maincanvasafterid)
            self.__maincanvasafterid = self.__maincanvas.after(120000, self.__showHome)
            self.zfuncs.action(deviceid, deviceaction)
            if self.__subcanvasafterid is not None:
                self.__subcanvas.after_cancel(self.__subcanvasafterid)
            self.__subcanvasafterid = self.__subcanvas.after(1500, drawsub, roomid)

        # Clear and setup canvas
        self.__clearMainCanvas()
        self.__clearSubCanvas()

        # Timeout after 120 seconds
        self.__maincanvasafterid = self.__maincanvas.after(120000, self.__showHome)

        # Display Z Menu Sub Buttons
        if (self.DISP_CONFIG["zwave"]["enabled"]):
            if (self.zfuncs is None):
                self.zfuncs = disp_zwavefuncs(self.__maincanvas, self.DISP_CONFIG["zwave"]["username"], self.DISP_CONFIG["zwave"]["password"], self.DISP_CONFIG["zwave"]["url"], self.DISP_CONFIG["zwave"]["tag"])
            roomList = self.zfuncs.getRooms(self.DISP_CONFIG["zwave"]["full"])
            buttonTop = 24
            for roomitem in roomList:
                if (roomitem["id"] == 0):
                    roomButtons = self.zfuncs.getRoomDevices(self.DISP_CONFIG["zwave"]["full"], roomitem["id"])
                    buttonTopSub = 30
                    for zDeviceItem in roomButtons:
                        if (zDeviceItem['deviceType'] == 'toggleButton'):
                            LcarsBlockSmall(self.__subcanvas, colours.CORAL, (290, buttonTopSub), zDeviceItem['metrics']["title"], width=180, handler=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.zfuncs.action(p1, p2))
                        elif (zDeviceItem['deviceType'] == 'switchBinary'):
                            if (zDeviceItem['metrics']['level'] == 'on'):
                                LcarsBlockSmall(self.__subcanvas, colours.GREEN, (290, buttonTopSub), zDeviceItem['metrics']["title"], width=180, handler=lambda p1 = zDeviceItem['id'], p2 = 'off' : self.zfuncs.action(p1, p2))
                            else:
                                LcarsBlockSmall(self.__subcanvas, colours.RED, (290, buttonTopSub), zDeviceItem['metrics']["title"], width=180, handler=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.zfuncs.action(p1, p2))
                        elif (zDeviceItem['deviceType'] == 'switchMultilevel'):
                            if (int(zDeviceItem['metrics']['level']) == 0):
                                LcarsBlockSmall(self.__subcanvas, colours.RED, (290, buttonTopSub), zDeviceItem['metrics']["title"], width=180, handler=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.zfuncs.action(p1, p2))
                            else:
                                LcarsBlockSmall(self.__subcanvas, colours.GREEN, (290, buttonTopSub), zDeviceItem['metrics']["title"], width=180, handler=lambda p1 = zDeviceItem['id'], p2 = 'off' : self.zfuncs.action(p1, p2))
                        buttonTopSub += 50

                if (roomitem["id"] != 0):
                    LcarsBlockMedium(self.__maincanvas, colours.PEACH, (14, buttonTop), roomitem["title"], width=160, handler=lambda p1 = roomitem["id"] : drawsub(p1))
                    roomSensors = self.zfuncs.getRoomSensors(self.DISP_CONFIG["zwave"]["full"], roomitem["id"])
                    LcarsText(self.__subcanvas, colours.BLACK, (2, buttonTop+22), getSensorTemp(roomSensors), size=1.2, width=10, bg_colour=colours.VIOLET, anchor=tk.E)
                    LcarsText(self.__subcanvas, colours.BLACK, (144, buttonTop+22), getSensorLux(roomSensors), size=1.2, width=10, bg_colour=colours.PURPLE, anchor=tk.E)
                    buttonTop += 66


    def __clearMainCanvas(self):
        # Clear existing canvas, if exists
        try:
            if self.__maincanvasafterid is not None:
                self.__maincanvas.after_cancel(self.__maincanvasafterid)
        except:
            pass
        try:
            if self.__maincanvas is not None:
                self.__maincanvas.destroy()
        except:
            pass
        # Create new main canvas
        self.__maincanvas = tk.Canvas(self.root, bg=colours.BLACK, width=660, height=300, borderwidth=0, highlightthickness=0)
        self.__maincanvas.hidden = 0
        self.__maincanvas.place(x=140, y=120, width=660, height=300)


    def __clearSubCanvas(self):
        """ Clear and recreate Sub Canvas """
        if self.__subcanvasafterid is not None:
            self.__subcanvas.after_cancel(self.__subcanvasafterid)
        if self.__subcanvas is not None:
            self.__subcanvas.destroy()
        # Create new sub canvas
        self.__subcanvas = tk.Canvas(self.__maincanvas, bg=colours.BLACK, width=480, height=300, borderwidth=0, highlightthickness=0)
        self.__subcanvas.hidden = 0
        self.__subcanvas.place(x=180, y=0, width=480, height=300)
