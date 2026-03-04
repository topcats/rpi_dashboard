# rpi_dashboard
# =================
# Data Source - Web Calendar (iCal) reader
# - WebCalItem: Web Calendar Event Data Item
# - app_webcal: Web iCal Downloader

import json
import time
import urllib.request
from datetime import date, datetime as dt, timezone
import zoneinfo
from icalendar import Calendar, Event

class WebCalItem():
    """ Single Calendar Item """

    def __init__(self, subject=''):
        """
        Creates clean Web Calendar Item
        :param subject: Event Subject
        """
        self.Id = ''
        self.Subject = subject
        self.Location = ''
        self.Start = ''
        self.End = ''
        self.Created = ''
        self.Body = ''

    def __readCreatedTime(self, timevalue):
        """
        Takes the Manual Read JSON Time value object (inc timezone) and outputs into POSIX
        :param timevalue: JSON Time value object
        :rtype: float
        """
        timevalue = str(timevalue)
        if timevalue.startswith("b"):
            timevalue = timevalue.replace("b", "").replace("'", "")
        if "T" in timevalue and  "00010101" not in timevalue:
            zoneUTC = zoneinfo.ZoneInfo("UTC")
            zoneLON = zoneinfo.ZoneInfo("Europe/London")
            dateUTC = dt.strptime(timevalue[:15],"%Y%m%dT%H%M%S")
            dateUTC.replace(tzinfo=zoneUTC)
            dateLOCAL = dateUTC.astimezone(zoneLON)
            return float(dateLOCAL.replace(tzinfo=zoneUTC).timestamp())
        else:
            return None


    def read(self, eventitem):
        self.Id = str(eventitem["UID"])
        #self.Subject = str(eventitem["SUMMARY"])
        self.Location = str(eventitem["LOCATION"])
        self.Start = float(time.mktime(eventitem.start.astimezone(timezone.utc).timetuple()))
        self.End = float(time.mktime(eventitem.end.astimezone(timezone.utc).timetuple()))
        self.Created = self.__readCreatedTime(eventitem["DTSTAMP"].to_ical())
        self.Body = {
                "contentType": "Text",
                "content": str(eventitem["DESCRIPTION"])}


    def getobj(self):
        return {
                "Id": self.Id,
                "Subject": self.Subject,
                "Location": self.Location,
                "Start": self.Start,
                "End": self.End,
                "Created": self.Created,
                "Body": self.Body
            }



class app_webcal():
    """ Application Lib, Web Calendar Download and process """

    _datapath = 'data/webcal_'

    def __init__(self):
        """
        Web Calendar Download
        """
        self._initdate = int(time.time())


    def process(self, webcalconfig=None):
        """
        Will Get the iCalendar data and format ready for saving.

        :return: Returns a recent calendar
        :rtype: dictionary
        """
        returndata = {'dt': self._initdate }
        eventitems = []

        # Check have config and enabled
        if webcalconfig is None:
            webcalconfig = {}
        if not 'url' in webcalconfig:
            webcalconfig['url'] = ""
        if not 'subject_filter' in webcalconfig:
            webcalconfig['subject_filter'] = ""
        if not 'subject_replacements' in webcalconfig:
            webcalconfig['subject_replacements'] = []
        if not 'subject_ignore' in webcalconfig:
            webcalconfig['subject_ignore'] = []

        if webcalconfig['url'] != "":
            try:
                wurl_to_call = webcalconfig['url']
                wurl_to_call = wurl_to_call.replace("webcal://", "http://")
                wrequest = urllib.request.Request(wurl_to_call)
                wresponse = urllib.request.urlopen(wrequest).read().decode('utf-8')
                if not wresponse:
                    raise Exception("No Response")

                webcalendar = Calendar.from_ical(wresponse)
                for webevent in webcalendar.events:
                    # Check for Ignore
                    itemignore = 0
                    for subjectignore in webcalconfig['subject_ignore']:
                        if subjectignore in webevent.get("SUMMARY"):
                            itemignore = 1
                    # Check if Subject matches any filters
                    if itemignore == 0 and (webcalconfig['subject_filter'] == "" or webcalconfig['subject_filter'] in webevent.get("SUMMARY")):
                        summary = webevent["SUMMARY"]
                        # Do subject Replacements
                        for replacement in webcalconfig['subject_replacements']:
                            summary = summary.replace(replacement['from'], replacement['to'])
                        summary = summary.strip()
                        if "subject_prefix" in webcalconfig:
                            summary = webcalconfig['subject_prefix'] + summary
                        calitem = WebCalItem(summary)
                        calitem.read(webevent)
                        eventitems.append(calitem.getobj())
            except Exception as ex:
                print("ERROR:app_webcal.process()", ex)

        # Return Data, even if blank
        returndata['events'] = sorted(eventitems, key = lambda x: (x['Start'], x['End']))
        return returndata
