# rpi_dashboard
# =================
# Data Source - O365 Tasks
# - TaskImportanceLevel:
# - TaskStatusLevel:
# - TaskItem:
# - app_tasks:

from O365 import Account, FileSystemTokenBackend
from util.helper_coding import helper_coding as helpcrypto
import json
import time
from datetime import date, datetime as dt
from enum import Enum


class TaskImportanceLevel(Enum):
    Normal = 'normal'
    Low = 'low'
    High = 'high'


class TaskStatusLevel(Enum):
    Completed = 'completed'
    NotStarted = 'notStarted'
    Deferred = 'deferred'
    InProgress = 'inProgress'
    WaitingOnOthers = 'waitingOnOthers'



class TaskItem():
    """ Single Task Item """

    def __init__(self):
        self.Id = ''
        self.Title = ''
        self.Status = TaskStatusLevel.NotStarted
        self.Importance = TaskImportanceLevel.Normal
        self.Created = ''
        self.LastModified = ''
        self.Body = ''
        self.CompletedDateTime = ''
        self.DueDateTime = ''
        self.ReminderDateTime = ''
        self.ChecklistItems = []
        self.Categories = []
        self.AssignedTo = ''


    def readmanual(self, item):
        self.Id = str(item['id'])
        self.Title = str(item['title'])
        if 'status' in item and item['status'] is not None:
            self.Status = str(item['status'])
        if 'importance' in item and item['importance'] is not None:
            self.Importance = str(item['importance'])
        if 'createdDateTime' in item and item['createdDateTime'] is not None:
            self.Created = float(time.mktime(time.strptime(item['createdDateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))
        if 'lastModifiedDateTime' in item and item['lastModifiedDateTime'] is not None:
            self.LastModified = float(time.mktime(time.strptime(item['lastModifiedDateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))
        if 'body' in item and item['body'] is not None:
            self.Body = item['body']
        if 'completedDateTime' in item and item['completedDateTime'] is not None:
            self.CompletedDateTime = float(time.mktime(time.strptime(item['completedDateTime']['dateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))#"2022-11-16T15:15:00.0000000"
        if 'dueDateTime' in item and item['dueDateTime'] is not None:
            self.DueDateTime = float(time.mktime(time.strptime(item['dueDateTime']['dateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))
        if 'reminderDateTime' in item and item['reminderDateTime'] is not None:
            self.ReminderDateTime = float(time.mktime(time.strptime(item['reminderDateTime']['dateTime'][:24],"%Y-%m-%dT%H:%M:%S.%f")))
        if 'categories' in item and item['categories'] is not None:
            self.Categories = item['categories']
        if 'checklistItems' in item and item['checklistItems'] is not None:
            self.ChecklistItems = item['checklistItems']

        #Manual Detect Assigned To
        if 'content' in self.Body and self.Body['content'] is not None:
            if self.Body['content'].__contains__("@Tristan"):
                self.AssignedTo = "Tristan"
                self.Body['content'] = self.Body['content'].replace("@Tristan", "")
            if self.Body['content'].__contains__("@Steph"):
                self.AssignedTo = "Steph"
                self.Body['content'] = self.Body['content'].replace("@Steph", "")
            if self.Body['content'].__contains__("@Robbie"):
                self.AssignedTo = "Robbie"
                self.Body['content'] = self.Body['content'].replace("@Robbie", "")


    def logerror(self, messagetext):
        """ Create Task Item using error message details """
        self.Id ='00001'
        self.Title = str(messagetext)
        self.Created = int(time.time())
        self.LastModified = int(time.time())


    def getobj(self):
        return {
                "Id": self.Id,
                "Title": self.Title,
                "Status": self.Status,
                "Importance": self.Importance,
                "Categories": self.Categories,
                "LastModified": self.LastModified,
                "Body": self.Body,
                "Completed": self.CompletedDateTime,
                "Due": self.DueDateTime,
                "Reminder": self.ReminderDateTime,
                "ChecklistItems": self.ChecklistItems,
                "AssignedTo": self.AssignedTo
            }



class app_tasks():
    """ Application Lib, will connect to O365 and obtain the Task Lists Menu """

    def __init__(self, config=None):
        """ Tasks List grabber

        :param config: O365 Configuration object
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'plaintext' in self._json_config:
            self._json_config['plaintext'] = False


    def process(self, siteconfig=None):
        """ Will Get the Tasks data and format read for saving.
        :return: Returns the full tasks List, excluding completed
        :rtype: dictionary
        """
        # Check have config and enabled
        # if siteconfig['refresh'] != 0:

        #     try:

        #         # Connect to O365 (O365 Account Logon)
        #         if self._json_config['plaintext'] == False:
        #             o365_credentials = (helpcrypto().decode(self._json_config['client_id']), helpcrypto().decode(self._json_config['client_secret']))
        #             o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=helpcrypto().decode(self._json_config['tenant_id']))
        #         else:
        #             o365_credentials = (self._json_config['client_id'], self._json_config['client_secret'])
        #             o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=self._json_config['tenant_id'])

        #         if not o365_account.is_authenticated:  # will check if there is a token and has not expired
        #             o365_account.authenticate()

        #         if o365_account.is_authenticated:
        #             returndata = {'dt': int(time.time())}


        #             o365_todo = o365_account.tasks()

        #             o365_todofolder = o365_todo.get_folder(folder_id=self._json_config['folderid'])
        #             folder = o365_todo.get_default_folder()
        #             new_task = folder.new_task()  # creates a new unsaved task 
        #             new_task.subject = 'Send contract to George Best'
        #             new_task.due = dt.datetime(2020, 9, 25, 18, 30) 
        #             new_task.save()

        #         else:
        #             # Return not a lot as not authenticated
        #             errormessage = TaskItem('Today', 'User authentication failure', 'O365')
        #             return {
        #                 'dt': int(time.time()),
        #                 "tasks": [errormessage.getobj()]
        #                     }

        #     except Exception as ex:
        #             errormessage = TaskItem('Today', 'Process Error', 'O365', ex)
        #             return {
        #                 'dt': int(time.time()),
        #                 "tasks": [errormessage.getobj()]
        #                     }
        # else:
        #     # Return not a lot as not enabled
        return {
            'dt': int(time.time()),
            "tasks": []
                }



    def processmanual(self, siteconfig=None, sourcedata=None):
        """ Will Get the Task data and format read for saving.
        :return: Returns a Tasks List
        :rtype: dictionary
        """
        returndata = {'dt': int(time.time())}
        # Check have config and enabled
        if siteconfig['refresh'] != 0:
            oitems = []

            try:
                for o365_task in sourcedata:
                    oitem = TaskItem()
                    oitem.readmanual(o365_task)
                    oitems.append(oitem.getobj())

            except Exception as ex:
                print("ERROR:app_tasks.processmanual()", ex)
                oitem = TaskItem()
                oitem.logerror("Error: " + str(ex))
                oitems.append(oitem.getobj())

            # Sort by date, and return
            #returndata['items'] = sorted(oitems, key = lambda x: (x['Completed'], x['Due'], x['Title']))
            #oitems.sort(key = lambda obj: (obj.firstname, [(-ord(c) for c in obj.lastname)]))

            returndata['items'] = oitems
        
        # Return Data, even if blank
        return returndata
