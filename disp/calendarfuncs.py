# rpi_dashboard
# =================
# Display Function: Calendar Data
# - CalendarItem : Data item
# - disp_calendarfuncs : GetToday

import json
import os
from datetime import datetime, timedelta
from disp.screens.ui import colours



class CalerdarItem():
    """ 
    Calendar Item
    """
    # Public Vars
    Subject = None
    Location = None
    Start = None
    End = None
    IsAllDay = None
    ShowAs = None
    Reminder = None
    Importance = None
    Categories = None


    def __init__(self, eventitem = None):
        """
        Load CalendarItem

        :param eventitem: Source Calendar Data
        :type eventitem: dict
        """

        if eventitem is not None:
            self.Subject = eventitem['Subject']
            self.Location = eventitem['Location']
            self.Start = eventitem['Start']
            self.End = eventitem['End']
            self.IsAllDay = eventitem['IsAllDay']
            self.ShowAs = eventitem['ShowAs']
            self.Reminder = eventitem['Reminder']
            self.Importance = eventitem['Importance']
            if 'Categories' in eventitem and eventitem['Categories'] is not None:
                self.Categories = []
                for item in eventitem['Categories']:
                    self.Categories.append(item)
        pass


    def StartTime(self):
        """
        Return Start Time as Datetime

        :return: Start Time
        :rtype: datetime
        """
        return datetime.fromtimestamp(self.Start)


    def EndTime(self):
        """
        Return End Time as Datetime

        :return: End Time
        :rtype: datetime
        """
        return datetime.fromtimestamp(self.End)


    def GetText(self):
        """
        Return Text for Calendar Item

        :return: Start Time HH:MM and Subject
        :rtype: string
        """
        if (self.IsAllDay):
            return "    \t" + self.Subject
        elif (self.StartTime().hour >= 10 and self.StartTime().hour < 20):
            return "          " + self.StartTime().strftime("%H:%M") + "\t" + self.Subject
        else:
            return "        " + self.StartTime().strftime("%H:%M") + "\t" + self.Subject


    def GetColour(self):
        """
        Return Colour for Calendar Item

        :return: Colour based on Categories
        :rtype: string
        """
        if ("Steph" in self.Categories):
            return colours.MAUVE
        elif ("Tristan" in self.Categories):
            return colours.ORANGE
        elif ("Robbie" in self.Categories):
            return colours.BLUEGREY
        elif ("House" in self.Categories):
            return colours.PEACH
        else:
            return colours.BLUE



class disp_calendarfuncs:
    """ Display Lib: Calendar Functions """

    def __init__(self, datapath, locationid):
        """
        Initialize Calendar Display Functions

        :param datapath: Path to Weather Data
        :type datapath: string
        :param locationid: Location ID for Site Data
        :type locationid: int
        """
        self.datapath = datapath
        self.locationid = locationid
        pass


    def getToday(self):
        """
        Load Calendar Data from File
        Return Calendar Items for today only, from -1hour onwards for 24 hrs
        Up to 1800 only show today, after show tomorrow as well
        but still include all-day events

        :return: Calendar Data
        :rtype: dict
        """
        eventitems = []
        try:
            # Time Now
            currentdatetime = datetime.now()
            currenttimestampfrom = int((currentdatetime - timedelta(hours=1)).timestamp())
            # if time after 1800, show tomorrow as well, otherwise just show today
            if (int(currentdatetime.strftime('%H')) > 18):
                currenttimestamptill = int((currentdatetime + timedelta(hours=22)).timestamp())
            else:
                currenttimestamptill = int((currentdatetime.replace(hour=23, minute=59, second=0, microsecond=0)).timestamp())

            currentFile = os.path.normpath(os.path.join(self.datapath, 'infopane_'+str(self.locationid)+'.json'))
            with open(currentFile, encoding='utf-8') as fp:
                json_obj = json.load(fp)

            for o365_event in json_obj['events']:
                calitem = CalerdarItem(o365_event)
                if (calitem.End > currenttimestampfrom and calitem.Start <= currenttimestamptill):
                    eventitems.append(calitem)

        except Exception as ex:
            print("ERROR:eDisplay.disp_calendarfuncs.getToday()", ex)

        # Return Data, even if blank
        return eventitems
