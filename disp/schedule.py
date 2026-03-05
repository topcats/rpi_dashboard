# rpi_dashboard
# =================
# Display Function: Schedule Data
# - disp_schedule : GetCurrent
#   Returns the style and brightness for the current time based on the schedule config, and any override that may be in place.

import time
import datetime

class disp_schedule:
    """ 
    Display Schedule Functions
    """

    __schedule = None

    def __init__(self, schedule):
        """
        Load Schedule system

        :param schedule: Schedule config data
        :type schedule: dict
        """
        self.__schedule = schedule


    def __getCurrentWeekday(self):
        """
        Takes the Current DateTime, and returns the weekday (PHP Style)

        :return: Current Weekday (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
        :rtype: int
        """
        currentdatetime = datetime.datetime.now()
        currentweekday = (currentdatetime.weekday()) + 1
        if (currentweekday == 7):
            currentweekday = 0
        return currentweekday


    def __convertTime(self, timetext):
        """
        Convert Time to Number

        :param timetext: Time as Text ie '12:30'
        :type timetext: string
        :return: Integer of hours and minutes
        :rtype: int
        """
        timetextsplit = timetext.split(':')
        return (int(timetextsplit[0])*60) + int(timetextsplit[1])


    def getCurrent(self):
        """
        Takes the Current DateTime, and finds the current Style and brightness from the schedule.
        Double checks for override

        Default is (0,0) if no schedule item matches
        :return: Style and Brightness
        :rtype: tuple(int, int)
        """

        # get current values
        currentweekday = self.__getCurrentWeekday()
        currentdatetime = datetime.datetime.now()
        currenttimeint = self.__convertTime(currentdatetime.strftime('%H:%M'))

        # Look for override
        if 'override' in self.__schedule and 'end' in self.__schedule['override']:
            endval = self.__schedule['override']['end']
            if endval is not None and (endval == -1 or int(endval) > int(currentdatetime.timestamp())):
                return (self.__schedule['override']['style'], self.__schedule['override']['brightness'])

        # cycle round schedules
        for scheduleitem in self.__schedule['list']:
            if currentweekday in scheduleitem['day']:
                if currenttimeint >= self.__convertTime(scheduleitem['start']) and currenttimeint < self.__convertTime(scheduleitem['stop']):
                    return (scheduleitem['style'], scheduleitem['brightness'])
        return (0,0)
