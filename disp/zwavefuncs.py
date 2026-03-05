# rpi_dashboard
# =================
# Display Function: zWave Data
# - disp_zwavefuncs : GetRooms, GetRoomName, GetRoomSensors, GetRoomDevices, addButton, showMenu, hideMenu, action

from util.helper_coding import helper_coding
from util.zWaveApi3 import zWaveApi3 as zWaveApi
import tkinter as tk
from tkinter import Canvas
import time

class disp_zwavefuncs:
    """ Display Lib: ZWave Functions """

    __root = None
    __zwavecanvas = None
    __bZMenu = None
    __username = ""
    __password = ""
    __url = ""
    __searchtag = ""
    __displaystyle = 0
    __displaydevices = []
    __roomList = []
    __roomUpdated = 0
    __deviceList = []
    __deviceUpdated = 0


    def __init__(self, canvasroot, username, password, url, searchtag):
        """
        Initialize ZWave Display Functions

        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param username: ZWave Username
        :type username: string
        :param password: ZWave Password (Encypted)
        :type password: string
        :param url: ZWave URL
        :type url: string
        :param searchtag: ZWave Device Search Tag
        :type searchtag: string
        """
        self.__root = canvasroot
        self.__username = username
        self.__password = password
        self.__url = url
        self.__searchtag = searchtag
        pass


    def __getPassword(self):
        """
        Decrypt ZWave Password

        :return: Decrypted ZWave Password
        :rtype: string
        """
        decryptedpassword = helper_coding().decode(self.__password)
        return decryptedpassword


    def __getLocation(self):
        """
        Get zWave Locations

        Will cache response for 5 minutes
        """
        # Update room list every 5 minutes
        if (self.__roomUpdated == 0 or self.__roomList == [] or (int(time.time()) - self.__roomUpdated) > 300):
            self.__roomUpdated = int(time.time())
            # Get rooms from ZWave API
            try:
                oZWave = zWaveApi(self.__username, self.__getPassword(), self.__url)
                self.__roomList = oZWave.getLocations()
            except Exception as ex:
                print("ERROR:eDisplay.disp_zwavefuncs.__getLocation", ex)
                self.__roomList = []


    def __getDevices(self):
        """
        Get zWave Devices
        Filtered by search tag in config
        
        Will cache response for 1 minutes
        """
        # Update device list every 1 minutes
        if (self.__deviceUpdated == 0 or self.__deviceList == [] or (int(time.time()) - self.__deviceUpdated) > 50):
            self.__deviceUpdated = int(time.time())
            self.__deviceList = []
            # Get devices from ZWave API
            try:
                oZWave = zWaveApi(self.__username, self.__getPassword(), self.__url)
                oZDevices = oZWave.getDevices()
                for zDeviceItem in oZDevices:
                    if (zDeviceItem['tags'].count(self.__searchtag) >0):
                        self.__deviceList.append(zDeviceItem)
            except Exception as ex:
                print("ERROR:eDisplay.disp_zwavefuncs.__getDevices", ex)
                self.__deviceList = []


    def showMenu(self):
        """
        Show the Zwave Popup Menu

        :param displaystyle: 1 for Silver, 0 for Gray
        :type displaystyle: int
        """

        if (self.__zwavecanvas is None):
            self.__zwavecanvas = Canvas(self.__root, bg='blue', borderwidth=2)
            self.__zwavecanvas.config(width=230, height=200)
            self.__zwavecanvas.place(x=(self.__root.winfo_width()-230), y=(self.__root.winfo_height()-200))

            if self.__displaystyle == 1:
                buttonbg = 'silver'
            else:
                buttonbg = 'gray'

            # Get Updated Devices List
            self.__getDevices()
            for zDeviceItem in self.__deviceList:
                if (zDeviceItem['id'] in self.__displaydevices):
                    if (zDeviceItem['deviceType'] == 'toggleButton'):
                        zwavecmdtb = tk.Button(self.__zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', bg=buttonbg, width=30, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.action(p1, p2))
                        zwavecmdtb.pack()
                    elif (zDeviceItem['deviceType'] == 'switchBinary'):
                        if (zDeviceItem['metrics']['level'] == 'on'):
                            zwavecmdsb = tk.Button(self.__zwavecanvas, text=zDeviceItem['metrics']["title"], fg='red', bg=buttonbg, width=30, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'off' : self.action(p1, p2))
                            zwavecmdsb.pack()
                        else:
                            zwavecmd = tk.Button(self.__zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', bg=buttonbg, width=30, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.action(p1, p2))
                            zwavecmd.pack()
                    elif (zDeviceItem['deviceType'] == 'switchMultilevel'):
                        if (int(zDeviceItem['metrics']['level']) == 0):
                            zwavecmd = tk.Button(self.__zwavecanvas, text=zDeviceItem['metrics']["title"], fg='green', bg=buttonbg, width=30, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'on' : self.action(p1, p2))
                            zwavecmd.pack()
                        else:
                            zwavecmd = tk.Button(self.__zwavecanvas, text=zDeviceItem['metrics']["title"], fg='red', bg=buttonbg, width=30, padx=1, pady=4, relief='flat', command=lambda p1 = zDeviceItem['id'], p2 = 'off' : self.action(p1, p2))
                            zwavecmd.pack()
            cx = (self.__root.winfo_width() - (self.__zwavecanvas.winfo_reqwidth() + 34))
            cy = (self.__root.winfo_height() - (self.__zwavecanvas.winfo_reqheight() + 6))
            self.__zwavecanvas.place(x=cx, y=cy)
            self.__zwavecanvas.after(12000, self.hideMenu)
        else:
            self.hideMenu()


    def hideMenu(self):
        """ Hide ZWave Menu Canvas """
        if (self.__zwavecanvas is not None):
            self.__zwavecanvas.delete("all")
            self.__zwavecanvas.place_forget()
            self.__zwavecanvas.destroy()
            self.__zwavecanvas = None


    def action(self, zID, zAction):
        """
        Do zWave Action.

        Will reset device cache,
        and also hide the menu (if valid)
        
        :param zID: Device ID
        :type zID: string
        :param zAction: Action to do
        :type zAction: string
        """
        try:
            oZWave = zWaveApi(self.__username, self.__getPassword(), self.__url)
            oZWave.setDeviceCommand(zID, zAction)
        except Exception as ex:
            print("ERROR:eDisplay.disp_zwavefuncs.action", ex)
        self.__deviceUpdated = 0
        self.hideMenu()


    def addButton(self, displaystyle=0, displaydevices=[]):
        """ 
        Add a ZWave Button to the Display
        
        :param displaystyle: Display Style (0=Night: Blue on Black, 1=Day: White on Blue)
        :type displaystyle: integer
        """

        # Remove existing button if it exists
        if self.__bZMenu is not None:
            # self.__bZMenu.delete("all")
            try:
                self.__bZMenu.place_forget()
                self.__bZMenu.destroy()
            except:
                pass
            self.__bZMenu = None

        # Add new button
        self.__displaydevices = displaydevices
        self.__displaystyle = displaystyle
        if displaystyle == 1:
            buttonfg = 'white'
            buttonbg = 'blue'
        else:
            buttonfg = 'blue'
            buttonbg = 'black'

        self.__bZMenu = tk.Button(self.__root, text='Z', pady=4, padx=4, font=('Helvetica', 14, 'bold'), fg=buttonfg, bg=buttonbg, activeforeground='white', activebackground='blue', command=self.showMenu)
        self.__bZMenu.place(x=(self.__root.winfo_width()-50), y=(self.__root.winfo_height()-50), width=30, height=30)


    def getRooms(self, display=[]):
        """
        Get ZWave Rooms

        :param display: Display config data
        :type display: dict
        :return: List of ZWave Rooms
        :rtype: list
        """

        # Parse display config for rooms to show
        displayRooms = []
        for item in display:
            displayRooms.append(item['room'])

        # Update Room Data
        self.__getLocation()

        # Limit room list to rooms in display config
        oRooms = []
        for oZRoom in self.__roomList:
            if (oZRoom['id'] in displayRooms):
                if (oZRoom['id'] == 0):
                    oZRoom['title'] = 'House'
                oRooms.append(oZRoom)

        return oRooms
    

    def getRoomName(self, roomid):
        """
        Get ZWave Room Name

        :param roomid: Room Location ID
        :type roomid: int
        :return: Room name or blank
        :rtype: string
        """

        # Update Room Data
        self.__getLocation()

        # Search
        for oZRoom in self.__roomList:
            if (oZRoom['id'] == roomid):
                if (oZRoom['id'] == 0):
                    return 'House'
                return oZRoom['title']
        return ""


    def getRoomSensors(self, display=[], room=0):
        """
        Get ZWave Sensors for a Room

        :param display: Display config data
        :type display: dict
        :param room: Room ID
        :type room: integer
        :return: List of ZWave Sensors for the Room
        :rtype: list
        """

        # Find Room data
        displayRoom = {}
        for item in display:
            if (item["room"] == room):
                displayRoom = item
        if (displayRoom == {} or "sensors" not in displayRoom):
            return []
        
        # Update Device Data
        self.__getDevices()

        # Limit device list to devices in the room
        oSensors = []
        for zDeviceItem in self.__deviceList:
            if (zDeviceItem['id'] in displayRoom['sensors']):
                oSensors.append(zDeviceItem)

        return oSensors


    def getRoomDevices(self, display=[], room=0):
        """
        Get ZWave Devices for a Room

        :param display: Display config data
        :type display: dict
        :param room: Room ID
        :type room: integer
        :return: List of ZWave Devices for the Room
        :rtype: list
        """

        # Find Room data
        displayRoom = {}
        for item in display:
            if (item["room"] == room):
                displayRoom = item
        if (displayRoom == {} or "devices" not in displayRoom):
            return []
        
        # Update Device Data
        self.__getDevices()

        # Limit device list to devices in the room
        oDevices = []
        for zDeviceItem in self.__deviceList:
            if (zDeviceItem['id'] in displayRoom["devices"]):
                oDevices.append(zDeviceItem)

        return oDevices
