# rpi_dashboard
# =================
# Data Source - O365 Calendar
# - MasterCategoryColorPreset: Calendar Master Category Colour Presets
# - CalendarItem: Calendar Data Object 
# - app_calendar: Main Calendar Reader

from O365 import Account, FileSystemTokenBackend
from O365.category import CategoryColor
from util.helper_coding import helper_coding as helpcrypto
import os
import json
import time
from datetime import date, datetime as dt, timedelta as dtd
import zoneinfo


class MasterCategoryColorPreset(object):
    """ Array for holding Category Colours """

    def __init__(self):
        """ Pre loads the class with the standard set of colours """
        self._colors = [
            {"outlookname": 'none',     "rgb": '255,255,255', "hex": '#FFFFFF'},
            {"outlookname": 'preset0',  "rgb": '240,125,136', "hex": '#F07D88'},
            {"outlookname": 'preset1',  "rgb": '255,140,0',   "hex": '#FF9509'},
            {"outlookname": 'preset2',  "rgb": '254,203,111', "hex": '#FECB6F'},
            {"outlookname": 'preset3',  "rgb": '255,241,0',   "hex": '#FFF100'},
            {"outlookname": 'preset4',  "rgb": '95,190,125',  "hex": '#5FBE7D'},
            {"outlookname": 'preset5',  "rgb": '51,186,177',  "hex": '#33BAB1'},
            {"outlookname": 'preset6',  "rgb": '163,179,103', "hex": '#A3B367'},
            {"outlookname": 'preset7',  "rgb": '85,171,229',  "hex": '#55ABE5'},
            {"outlookname": 'preset8',  "rgb": '168,149,226', "hex": '#A895E2'},
            {"outlookname": 'preset9',  "rgb": '228,139,181', "hex": '#E48BB5'},
            {"outlookname": 'preset10', "rgb": '185,192,203', "hex": '#B9C0CB'},
            {"outlookname": 'preset11', "rgb": '76,89,110',   "hex": '#4C596E'},
            {"outlookname": 'preset12', "rgb": '171,171,171', "hex": '#ABABAB'},
            {"outlookname": 'preset13', "rgb": '102,102,102', "hex": '#666666'},
            {"outlookname": 'preset14', "rgb": '71,71,71',    "hex": '#474747'},
            {"outlookname": 'preset15', "rgb": '145,10,25',   "hex": '#910A19'},
            {"outlookname": 'preset16', "rgb": '206,75,40',   "hex": '#CE4B28'},
            {"outlookname": 'preset17', "rgb": '153,110,54',  "hex": '#996E36'},
            {"outlookname": 'preset18', "rgb": '176,169,35',  "hex": '#B0A923'},
            {"outlookname": 'preset19', "rgb": '2,104,2',     "hex": '#026802'},
            {"outlookname": 'preset20', "rgb": '28,99,103',   "hex": '#1C6367'},
            {"outlookname": 'preset21', "rgb": '92,106,34',   "hex": '#5C6A22'},
            {"outlookname": 'preset22', "rgb": '37,64,105',   "hex": '#254069'},
            {"outlookname": 'preset23', "rgb": '86,38,133',   "hex": '#562685'},
            {"outlookname": 'preset24', "rgb": '128,39,93',   "hex": '#80275D'}
        ]

    def get_item_fromoutlook(self, name):
        """ Finds the whole sub object by Outlook Name """
        for c in self._colors:
            if c['outlookname'] == name.lower():
                return c



class CalendarItem():
    """ Single Calendar Item """

    def __init__(self, calendarname=''):
        """ Creates clean Calendar Item, with the Calendar Name
        :param calendarname: O365 Calendar Name
        """
        self.CalendarName = calendarname
        self.Id = ''
        self.Ical = ''
        self.Subject = ''
        self.Location = ''
        self.Organizer = ''
        self.Start = ''
        self.End = ''
        self.IsAllDay = False
        self.ShowAs = ''
        self.Reminder = False
        self.Importance = ''
        self.Categories = []
        self.Sensitivity = ''
        self.Created = ''
        self.SeriesMasterId = None
        self.Recurrence = None
        self.Body = ''


    def read(self, eventitem):
        self.Id = str(eventitem.object_id)
        self.Ical = str(eventitem.ical_uid)
        self.Subject = str(eventitem.subject)
        self.Location = str(eventitem.location.get('displayName', ''))
        self.Organizer = str(eventitem.organizer.name)
        self.Start = float(time.mktime(eventitem.start.timetuple()))
        self.End = float(time.mktime(eventitem.end.timetuple()))
        self.IsAllDay = bool(eventitem.is_all_day)
        self.ShowAs = str(eventitem.show_as.value)
        self.Reminder = bool(eventitem.is_reminder_on)
        self.Importance = str(eventitem.importance.value)
        self.Categories = eventitem.categories
        self.Sensitivity = str(eventitem.sensitivity.value)
        self.Created = float(time.mktime(eventitem.created.timetuple()))
        self.Body = {
                "contentType": eventitem.body_type,
                "content": eventitem.body}
        if eventitem.series_master_id is not None:
            self.SeriesMasterId = eventitem.series_master_id
            self.Recurrence = { "type": str(eventitem.event_type.value) }


    def __readmanualtime(self, timevalue):
        """ Takes the Manual Read JSON Time value object (inc timezone) and outputs into POSIX
        :param timevalue: JSON Time value object
        :return: Time as a number
        :rtype: float
        """
        if timevalue['timeZone'] == 'UTC':
            zoneUTC = zoneinfo.ZoneInfo("UTC")
            zoneLON = zoneinfo.ZoneInfo("Europe/London")
            dateUTC = dt.strptime(timevalue['dateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")
            dateUTC.replace(tzinfo=zoneUTC)
            dateLOCAL = dateUTC.astimezone(zoneLON)
            return float(dateLOCAL.replace(tzinfo=zoneUTC).timestamp())
        else:
            # "2022-11-16T15:15:00.0000000"
            return float(time.mktime(time.strptime(timevalue['dateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))


    def readmanual(self, eventitem):
        self.Id = str(eventitem['id'])
        self.Ical = str(eventitem['iCalUId'])
        self.Subject = str(eventitem['subject'])
        self.Location = str(eventitem['location']['displayName'])
        self.Organizer = str(eventitem['organizer']['emailAddress']['name'])
        self.Start = self.__readmanualtime(eventitem['start'])
        self.End = self.__readmanualtime(eventitem['end'])
        self.IsAllDay = bool(eventitem['isAllDay'])
        self.ShowAs = str(eventitem['showAs'])
        self.Reminder = bool(eventitem['isReminderOn'])
        self.Importance = str(eventitem['importance'])
        self.Categories = eventitem['categories']
        self.Sensitivity = str(eventitem['sensitivity'])
        self.Created = float(time.mktime(time.strptime(eventitem['createdDateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))
        self.Body = eventitem['body']
        if eventitem['seriesMasterId'] is not None:
            self.SeriesMasterId = eventitem['seriesMasterId']
            self.Recurrence = { "type": str(eventitem['type']),
                               "text": eventitem['recurrence']}

        if eventitem['attachments'] is not None and len(eventitem['attachments']) > 0:
            for eventitemattachment in eventitem['attachments']:
                if eventitemattachment['isInline'] == True and eventitem['body'] is not None:
                    self.Body['content'] = self.Body['content'].replace("originalSrc=\"cid:" + eventitemattachment['contentId'] + "\"", " ")
                    self.Body['content'] = self.Body['content'].replace("data-imagetype=\"AttachmentByCid\"", " ")
                    self.Body['content'] = self.Body['content'].replace("src=\"cid:" + eventitemattachment['contentId'] + "\"", "src=\"data:" + eventitemattachment['contentType'] + ";base64," + eventitemattachment['contentBytes'] + "\"")


    def logerror(self, messagetext):
        """ Create Caledar Item using error message details
        :param messagetext: Error Message to use in Subject
        """
        self.Id ='00001'
        self.Ical = '00001'
        self.Subject = str(messagetext)
        self.Start = time.mktime(dt.now().date().timetuple())
        self.End = time.mktime((dt.now().date() + dtd(days=+7)).timetuple())
        self.IsAllDay = True
        self.ShowAs = 'busy'
        self.Reminder = True
        self.Importance = 'normal'
        self.Sensitivity = 'normal'
        self.Created = int(time.time())


    def getobj(self):
        """ Get the Calendar Details as json object
        :return: Details as required
        :rtype: json
        """
        return {
                "CalendarName": self.CalendarName,
                "Id": self.Id,
                "Ical": self.Ical,
                "Subject": self.Subject,
                "Location": self.Location,
                "Organizer": self.Organizer,
                "Start": self.Start,
                "End": self.End,
                "IsAllDay": self.IsAllDay,
                "ShowAs": self.ShowAs,
                "Reminder": self.Reminder,
                "Importance": self.Importance,
                "Categories": self.Categories,
                "Sensitivity": self.Sensitivity,
                "Created": self.Created,
                "SeriesMasterId": self.SeriesMasterId,
                "Recurrence": self.Recurrence,
                "Body": self.Body
            }



class app_calendar():
    """ Application Lib: Calendar, will connect to O365 and obtain Calendar Information """

    datapath = 'data/calendar/'
    _tokenpath = 'data/'
    _tokenfilename = 'o365_token.json'


    def __init__(self, config=None):
        """ Calendar Information grabber
        :param config: O365 Configuration object
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'plaintext' in self._json_config:
            self._json_config['plaintext'] = False

        self._categorylist = []


    def process(self, siteconfig=None):
        """ Will Get the Calendar data and format read for saving.
        :return: Returns a recent calendar
        :rtype: dictionary
        """
        returndata = {'dt': int(time.time())}
        # Check have config and enabled
        if siteconfig['refresh'] != 0:
            eventitems = []
            try:
                # Connect to O365 (O365 Account Logon)
                o365_tokenbackend = FileSystemTokenBackend(token_path=self._tokenpath, token_filename=self._tokenfilename)
                if self._json_config['plaintext'] == False:
                    o365_credentials = (helpcrypto().decode(self._json_config['client_id']), helpcrypto().decode(self._json_config['client_secret']))
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=helpcrypto().decode(self._json_config['tenant_id']), token_backend=o365_tokenbackend)
                else:
                    o365_credentials = (self._json_config['client_id'], self._json_config['client_secret'])
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=self._json_config['tenant_id'], token_backend=o365_tokenbackend)

                if not o365_account.is_authenticated:  # will check if there is a token and has not expired
                    o365_account.authenticate()

                if o365_account.is_authenticated:
                    o365_timefrommorning = dt.now().date() + dtd(days=int(siteconfig['days_past']))
                    o365_timetillmorning = dt.now().date() + dtd(days=int(siteconfig['days_future']))
                    #print("o365_timefrommorning :", o365_timefrommorning)
                    #print("o365_timetillmorning :", o365_timetillmorning)

                    if self._json_config['plaintext'] == False:
                        # Pre Load Master Category list
                        self.__get_categorylist(o365_account, helpcrypto().decode(siteconfig['useremail']))

                        # Loop thou calendars
                        o365_schedule = o365_account.schedule(resource=helpcrypto().decode(siteconfig['useremail']))
                    else:
                        # Pre Load Master Category list
                        self.__get_categorylist(o365_account, siteconfig['useremail'])

                        # Loop thou calendars
                        o365_schedule = o365_account.schedule(resource=siteconfig['useremail'])

                    for o365_calendar in o365_schedule.list_calendars():
                        if o365_calendar.name in siteconfig['calendars'] or '*' in siteconfig['calendars']:
                            # print('C  ', o365_calendar.name)

                            # New Version
                            # o365_calendarQuery = o365_calendar.new_query()
                            # o365_calendarQuerystart = o365_calendarQuery.greater_equal('start', o365_timefrommorning)
                            # o365_calendarQueryend = o365_calendarQuery.less_equal('end', o365_timetillmorning)
                            # o365_mycalendarEvents = o365_calendar.get_events(limit=200, include_recurring=True, start_recurring=o365_calendarQuerystart, end_recurring=o365_calendarQueryend)
                            # Old Version
                            o365_calendarQuery = o365_calendar.new_query('start').greater_equal(o365_timefrommorning)
                            o365_calendarQuery.chain('and').on_attribute('end').less_equal(o365_timetillmorning)
                            o365_mycalendarEvents = o365_calendar.get_events(limit=200, query=o365_calendarQuery, include_recurring=True)
                            for o365_event in o365_mycalendarEvents:
                                # print('E  ', o365_event.start, o365_event.end, o365_event.subject)
                                calitem = CalendarItem(calendarname=o365_calendar.name)
                                calitem.read(o365_event)
                                if calitem.SeriesMasterId is not None:
                                    calitem.Recurrence['text'] = self.__get_recurance(o365_calendar, calitem.SeriesMasterId)
                                self.__process_categories(calitem)
                                eventitems.append(calitem.getobj())
                else:
                    raise Exception("O365 Authentication Required")

            except Exception as ex:
                print("ERROR:app_calendar.process()", ex)
                calitem = CalendarItem("Calendar")
                calitem.logerror("Error: " + str(ex))
                eventitems.append(calitem.getobj())

            # Sort by date, and return
            returndata['events'] = sorted(eventitems, key = lambda x: (x['Start'], x['End']))

        # Return Data, even if blank
        return returndata


    def processmanual(self, siteconfig=None, sourcedata=None):
        """ Will Get the Calendar data and format read for saving.
        :return: Returns a recent calendar
        :rtype: dictionary
        """
        returndata = {'dt': int(time.time())}
        # Check have config and enabled
        if siteconfig['refresh'] != 0:
            eventitems = []

            try:
                for o365_event in sourcedata:
                    calitem = CalendarItem(calendarname="Calendar")
                    calitem.readmanual(o365_event)
                    self.__process_categories(calitem)
                    eventitems.append(calitem.getobj())

            except Exception as ex:
                print("ERROR:app_calendar.processmanual()", ex)
                calitem = CalendarItem("Calendar")
                calitem.logerror("Error: " + str(ex))
                eventitems.append(calitem.getobj())

            # Sort by date, and return
            returndata['events'] = sorted(eventitems, key = lambda x: (x['Start'], x['End']))

        # Return Data, even if blank
        return returndata


    def __get_recurance(self, calendar, eventID):
        """ Finds a Calendar Event and returns the Recurrance """
        o365_calMasterItem = calendar.get_event(eventID)
        return str(o365_calMasterItem.recurrence)


    def __get_categorylist(self, accountitem, resourcename=''):
        self._categorylist = []
        try:
            o365_accountoc = accountitem.outlook_categories(resource=resourcename)
            for o365_category in o365_accountoc.get_categories():
                mastercolor = MasterCategoryColorPreset().get_item_fromoutlook(o365_category.color.value)
                self._categorylist.append({
                    "id": o365_category.object_id,
                    "displayName": o365_category.name,
                    "color": {
                        "outlookname": o365_category.color.value,
                        "name": o365_category.color.name,
                        "rgb": mastercolor['rgb'],
                        "hex": mastercolor['hex']
                    }
                })
        except Exception as ex:
            print("ERROR:app_calendar.__get_categorylist()", ex)
            self._categorylist = []


    def set_categorylist(self, categorylist=None):
        self._categorylist = []
        try:
            for local_category in categorylist:
                mastercolor = MasterCategoryColorPreset().get_item_fromoutlook(local_category['color'])
                self._categorylist.append({
                    "id": local_category['id'],
                    "displayName": local_category['displayName'],
                    "color": {
                        "outlookname": local_category['color'],
                        "name": local_category['color'],
                        "rgb": mastercolor['rgb'],
                        "hex": mastercolor['hex']
                    }
                })
        except Exception as ex:
            print("ERROR:app_calendar.set_categorylist()", ex)
            self._categorylist = []


    def __process_categories(self, calitem: CalendarItem):
        """ Adds Master Category data to Calendar Item Category """
        try:
            newCategories = {}
            for retcatitem in calitem.Categories:
                newCategoriesItem = {}
                if len(self._categorylist) == 0:
                    basecolor = MasterCategoryColorPreset().get_item_fromoutlook('none')
                    newCategoriesItem['outlookname'] = basecolor['outlookname']
                    newCategoriesItem['hex'] = basecolor['hex']
                else:
                    coloritem = [item['color'] for item in self._categorylist
                        if item['displayName'] == retcatitem][0]
                    newCategoriesItem['outlookname'] = coloritem['outlookname']
                    newCategoriesItem['hex'] = coloritem['hex']
                newCategories[retcatitem] = newCategoriesItem

        except Exception as ex:
            print("ERROR:app_calendar.__process_categories() " + calitem.Id, ex)
            newCategories = calitem.Categories

        # Update
        calitem.Categories = newCategories


    def savedata(self, filename, jsondata):
        """ Save json Infomation
        :param filename: path and filename (excluding json)
        :param jsondata: Json Information
        """

        try:
            with open(self.datapath + str(filename) + '.json', 'w', encoding='utf-8') as fp:
                json.dump(jsondata, fp)

        except Exception as ex:
            print('ERROR:app_calendar.savedata('+filename+')', ex)


    def loaddata(self, filename):
        """ Load json Infomation
        :param filename: path and filename (excluding json)
        :return: Returns the file data
        :rtype: dictionary
        """

        json_obj = {}
        try:
            if os.path.isfile(self.datapath + str(filename) + '.json'):
                with open(self.datapath + str(filename) + '.json', encoding='utf-8') as fp:
                    json_obj = json.load(fp)
            else: 
                print("file not found", filename)
        except Exception as ex:
            print('ERROR:app_calendar.loaddata('+filename+')', ex)
        return json_obj
