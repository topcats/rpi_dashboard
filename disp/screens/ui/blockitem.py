# rpi_dashboard
# =================
# LCARS Text Class
# - LcarsText: Text that can be placed anywhere, with optional clock and date modes

import tkinter as tk
import tkinter.font as tkFont
import time
from disp.screens.ui import colours

class LcarsText():
    """Text that can be placed anywhere"""

    root = None
    textItem = None
    clockformat = '%H:%M:%S'
    dateformat = '%A %d %b %Y'

    def __init__(self, canvasroot, colour, pos, text, size=1.0, bg_colour = colours.BLACK, anchor=tk.W, width=None):
        """
        Init Text Item

        :param canvasroot: Root Canvas
        :type canvasroot: tkinter.Tk
        :param colour: Text Colour (Foreground)
        :type colour: string
        :param pos: Text Position (x, y)
        :type pos: tuple
        :param text: Label Text
        :type text: string
        :param size: Text size multiplier
        :type size: float
        :param bg_colour: Background Colour (default black)
        :type bg_colour: string
        :param anchor: Anchor Point
        :type anchor: Literal["nw", "n", "ne", "w", "center", "e", "sw", "s", "se"] = "W",
        """
        # Capture the parameters
        self.root = canvasroot
        self.colour = colour
        self.bgcolour = bg_colour
        self.pos = pos
        self.text = text
        self.anchor = anchor
        self.width = width
        #self.font = tkFont.Font("assets/swiss911.ttf", int(19.0 * size))
        self.font = ("Tungsten Bold", int(20*size), 'normal')
        self.buttontItem = tk.Label(
                                self.root,
                                text=self.text,
                                font=self.font,
                                background=self.bgcolour,
                                fg=self.colour,
                                anchor=self.anchor,
                                justify='left',
                                pady=0,
                                padx=0,
                                highlightthickness=0,
                                borderwidth=0
                            )
        self.buttontItem.place(x=self.pos[0], y=self.pos[1])
        if self.width is not None:
            self.buttontItem.config(width=self.width)


    def setText(self, newText):
        """
        Update Item Test

        :param newText: Path to Weather Data
        :type newText: string
        """
        self.root.itemconfig(self.textItem, text=newText)


    def isClock(self):
        """
        Set the Item to be a clock time and update every second
        """
        # Clock Time Loop
        self.anchor = tk.E
        self.buttontItem.config(anchor=tk.E)
        self.tick_time1 = time.strftime(self.clockformat)
        self.buttontItem.config(text=self.tick_time1)
        self.buttontItem.after(200, self.__clockTimeUpdate)


    def isDate(self):
        """
        Set the Item to be a date and update every second
        """
        # Clock Date Loop
        self.blnflag = True
        self.anchor = tk.CENTER
        self.buttontItem.config(width=28)
        self.buttontItem.config(anchor=tk.CENTER)
        self.buttontItem.config(text=time.strftime(self.dateformat))
        self.buttontItem.after(20000, self.__clockDateUpdate)


    def __clockTimeUpdate(self):
        """
        Update the Clock Display every second.
        """
        try:
            # get the current local time from the PC
            tick_time2 = time.strftime(self.clockformat)
            # if time string has changed, update it
            if tick_time2 != self.tick_time1:
                self.tick_time1 = tick_time2
                self.buttontItem.config(text=tick_time2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            self.buttontItem.after(200, self.__clockTimeUpdate)
        except Exception as ex:
            print("ERROR:eDisplay.blockitem.__clockTimeUpdate()", ex)
            return 'Call updating clock time, try again'
        

    def __clockDateUpdate(self):
        """
        Update the Date Display every 30 minutes.
        """
        try:
            # get the current local time from the PC
            tick_time2 = time.strftime(self.clockformat)
            # if time string has changed, update it
            min2=tick_time2.split(':')
            if (min2[1]=='30' or min2[1]=='00') and self.blnflag==True:
                #Update Date
                self.buttontItem.config(text=time.strftime(self.dateformat))
                self.blnflag = False
            elif min2[1]!='30' and min2[1]!='00':
                self.blnflag = True

            self.buttontItem.after(20000, self.__clockDateUpdate)
        except Exception as ex:
            print("ERROR:eDisplay.DayScblockitemreen.__clockDateUpdate()", ex)
            return 'Call updating clock date, try again'
