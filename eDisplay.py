#!/usr/bin/python3
# rpi_dashboard
# =================
# Display Screen

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

# IMPORTS
import socket
import os
import tkinter as tk
from PIL import Image, ImageTk
import time
from tkinter import Frame, Canvas
from disp.conf import disp_conf
from disp.rpifuncs import disp_rpifuncs
from disp.schedule import disp_schedule

# Swap to working folder
os.chdir('/home/pi/dashdisplay')

# GLOBAL VARIABLES
CONFIG_FILENAME = 'conf/display.json'
DISP_CONFIG = []
curstyle = -1
curbrightness = -1

def initDisplay():
    """ Initialize Display Settings """
    global root

    # Initialize Root Window
    root = tk.Tk()
    root.title("eDisplay")
    root.geometry("800x480+50+50")
    root.configure(background='black')
    root.resizable(False, False)
    if (socket.gethostname() == "rpi-2hp"):
        root.attributes('-fullscreen', True)
        root.attributes('-topmost', True)
        root.configure(cursor='none')
    pass

def processSchedule():
    """
    Process the Schedule

    Fired every minute to check for style/brightness changes.
    """
    global root
    global curstyle
    global curbrightness
    global DISP_CONFIG

    # Reload config
    DISP_CONFIG = disp_conf(CONFIG_FILENAME).loadConfig()

    # Check Schedule
    schedule = disp_schedule(DISP_CONFIG['schedule'])
    style, brightness = schedule.getCurrent()

    # Update Style (if different)
    if (style != curstyle):
        # Clear existing widgets
        root.unbind('<Escape>')
        for widget in root.winfo_children():
            widget.destroy()
        # Apply Style Change Here
        curstyle = style
        if style == 0:
            from disp.screens.nightscreen import NightScreen
            NightScreen(root, DISP_CONFIG, cmdCloseNow).showDisplay()
        if style == 1:
            from disp.screens.dayscreen import DayScreen
            DayScreen(root, DISP_CONFIG, cmdCloseNow).showDisplay()
        if style == 2:
            from disp.screens.fullscreen import FullScreen
            FullScreen(root, DISP_CONFIG, cmdCloseNow).showDisplay()

    if (brightness != curbrightness):
        # Apply Brightness Change Here
        if brightness == 0:
            disp_rpifuncs().screenOff()
        else:
            if curbrightness == 0:
                disp_rpifuncs().screenOn()
            disp_rpifuncs().setBrightness(brightness)
        curbrightness = brightness

    # Snooze for 1 minute
    root.after(60000, processSchedule)


def cmdCloseNow(self=None):
    """ Close the Display Application """
    global root
    print('Closing now...')
    root.destroy()
    time.sleep(1)


# MAIN PROGRAM
initDisplay()
root.after(500, processSchedule)
root.mainloop()
