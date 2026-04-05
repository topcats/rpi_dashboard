# rpi_dashboard
# =================
# Display Function: Calendar Data
# - CalendarItem : Data item
# - disp_calendarfuncs : GetToday

import json
import os
from datetime import datetime, timedelta


class CalerdarItem():

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
        return datetime.fromtimestamp(self.Start)


    def EndTime(self):
        return datetime.fromtimestamp(self.End)



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
            currenttimestampfromday = int((currentdatetime.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp())
            currenttimestampfrom = int((currentdatetime - timedelta(hours=1)).timestamp())
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
