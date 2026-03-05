# rpi_dashboard
# =================
# Data Source - Menu Management
# - app_menu: O365 Excel Reader and updater
# - DinnerMenuItem: Menu Data Item
# - DinnerOptionItem: Menu Option Data Item

from O365 import Account
from O365.utils import FileSystemTokenBackend
from O365.excel import WorkBook
from util.helper_coding import helper_coding as helpcrypto
import os
import json
import time
from datetime import date, datetime as dt
import requests
import base64

class app_menu():
    """ Application Lib: Menu, will connect to O365 and obtain the Dinner Menu from Excel """

    datapath = 'data/menu/'
    _tokenpath = 'data/'
    _tokenfilename = 'o365_token.json'


    def __init__(self, config=None):
        """
        Dinner Menu grabber
        
        :param config: O365 Configuration object
        :type config: dictionary
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'plaintext' in self._json_config:
            self._json_config['plaintext'] = False


    def process(self, siteconfig=None):
        """
        Will Get the Menu data and format read for saving.
        
        :param siteconfig: Site Config Data
        :type siteconfig: dictionary
        :return: Returns the full menu
        :rtype: dictionary
        """
        # Check have config and enabled
        if siteconfig['refresh'] != 0:

            try:
                # Connect to O365 (O365 Account Logon)
                o365_tokenbackend = FileSystemTokenBackend(token_path=self._tokenpath, token_filename=self._tokenfilename)
                if self._json_config['plaintext'] == False:
                    o365_credentials = (helpcrypto().decode(self._json_config['client_id']), helpcrypto().decode(self._json_config['client_secret']))
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=helpcrypto().decode(self._json_config['tenant_id']), token_backend=o365_tokenbackend)
                else:
                    o365_credentials = (self._json_config['client_id'], self._json_config['client_secret'])
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=self._json_config['tenant_id'], token_backend=o365_tokenbackend)

                # will check if there is a token and has not expired
                if not o365_account.is_authenticated:  
                    o365_account.authenticate()

                if o365_account.is_authenticated:
                    returndata = {'dt': int(time.time())}

                    # Connect to Storage Drive, and get file
                    if self._json_config['plaintext'] == False:
                        o365_storagedrive = o365_account.storage().get_drive(helpcrypto().decode(siteconfig['driveid']))
                        o365_storagedrivefile = o365_storagedrive.get_item(helpcrypto().decode(siteconfig['itemid']))
                    else:
                        o365_storagedrive = o365_account.storage().get_drive(siteconfig['driveid'])
                        o365_storagedrivefile = o365_storagedrive.get_item(siteconfig['itemid'])
                    returndata['modified'] = o365_storagedrivefile.modified.strftime("%a %d %b, %H:%M")
                    returndata['modifiedby'] = str(o365_storagedrivefile.modified_by)

                    # Open Excel File, and worksheet
                    o365_excelfile = WorkBook(o365_storagedrivefile, persist=False)
                    o365_excelfilews = o365_excelfile.get_worksheet(siteconfig['sheetname'])

                    # Loop Thou rows, till end
                    o365_timethismorning = (dt.now().date() - date(year=1900, month=1, day=1)).days + 2
                    returndata['menu'] = []
                    dataend = False
                    datarow_start = 2
                    while not dataend:
                        time.sleep(1)
                        datarows = o365_excelfilews.get_range('A' + str(datarow_start) + ':E' + str(datarow_start+30))
                        datarow_index = 0
                        while datarow_index < 30:
                            if not datarows or datarows.text[datarow_index][0] == '':
                                datarow_index = 500
                                dataend = True
                            else:
                                newItem = DinnerMenuItem()
                                newItem.readrows(datarows,datarow_index)
                                if int(datarows.values[datarow_index][0]) == o365_timethismorning:
                                    # number of days between the 01/01/1900
                                    newItem.today = True
                                if int(datarows.values[datarow_index][0]) >= (o365_timethismorning-1) and int(datarows.values[datarow_index][0]) <= (o365_timethismorning+7):
                                    returndata['menu'].append(newItem.getobj())
                            datarow_index += 1

                        if datarow_start >= 400:
                            #Catchment incase :)
                            print("ERROR:app_menu.process() Max Rows")
                            dataend = True
                        datarow_start += 30
                    return returndata
                else:
                    # Return not a lot as not authenticated
                    errormessage = DinnerMenuItem('Today', 'User authentication failure', 'O365')
                    return {
                        'dt': int(time.time()),
                        'modified': '',
                        'modifiedby': '',
                        "menu": [errormessage.getobj()]
                            }

            except Exception as ex:
                    errormessage = DinnerMenuItem('Today', 'Process Error', 'O365', ex)
                    print("ERROR:app_menu.process()", ex)
                    return {
                        'dt': int(time.time()),
                        'modified': '',
                        'modifiedby': '',
                        "menu": [errormessage.getobj()]
                            }
        else:
            # Return not a lot as not enabled
            return {
                'dt': int(time.time()),
                'modified': '',
                'modifiedby': '',
                "menu": []
                    }


    def getEditOptions(self, siteconfig=None):
        """
        Will Get the Menu Options and Chefs
        
        :param siteconfig: Site Config Data
        :type siteconfig: dictionary
        :return: Returns the 2 lists
        :rtype: dictionary
        """
        # Check have config and enabled
        if siteconfig['refresh'] != 0 and siteconfig['allowedit']:
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
                    returndata = {'dt': int(time.time())}
                    returndata['option'] = []
                    returndata['chef'] = []

                    # Connect to Storage Drive, and get file
                    if self._json_config['plaintext'] == False:
                        o365_storagedrive = o365_account.storage().get_drive(helpcrypto().decode(siteconfig['driveid']))
                        o365_storagedrivefile = o365_storagedrive.get_item(helpcrypto().decode(siteconfig['itemid']))
                    else:
                        o365_storagedrive = o365_account.storage().get_drive(siteconfig['driveid'])
                        o365_storagedrivefile = o365_storagedrive.get_item(siteconfig['itemid'])

                    # Open Excel File, and worksheet
                    o365_excelfile = WorkBook(o365_storagedrivefile, persist=False)

                    # Loop Thou menu option rows, till end
                    o365_excelfilews = o365_excelfile.get_worksheet(siteconfig['optionsheetname'])
                    dataend = False
                    datarow_start = 1
                    while not dataend:
                        time.sleep(1)
                        datarows = o365_excelfilews.get_range('A' + str(datarow_start) + ':D' + str(datarow_start+10))
                        datarow_index = 0
                        while datarow_index < 10:
                            if not datarows or datarows.text[datarow_index][0] == '':
                                datarow_index = 20
                                dataend = True
                            else:
                                newItem = DinnerOptionItem()
                                newItem.readrows(datarows,datarow_index)
                                returndata['option'].append(newItem.getobj())
                            datarow_index += 1

                        if datarow_start >= 200:
                            #Catchment incase :)
                            print("app_menu.getEditOptions() Max Rows Error")
                            dataend = True
                        datarow_start += 10

                    # Mass grab chef options rows, then loop thou
                    time.sleep(1)
                    o365_excelfilews = o365_excelfile.get_worksheet(siteconfig['chefsheetname'])
                    time.sleep(0.5)
                    datasheet = o365_excelfilews.get_range('A1:A10')
                    dataend = False
                    datarow_index = 0
                    while not dataend:
                        time.sleep(0.1)
                        if not datasheet or datasheet.text[datarow_index][0] == '':
                            dataend = True
                        else:
                            returndata['chef'].append(datasheet.text[datarow_index][0])
                        if datarow_index >= 10:
                            #Catchment incase :)
                            print("app_menu.getEditOptions() Max Rows Error")
                            dataend = True
                        datarow_index += 1

                    return returndata
                else:
                    # Return not a lot as not authenticated
                    errormessage = DinnerMenuItem('Today', 'User authentication failure', 'O365')
                    return {
                        'dt': int(time.time()),
                        'option': [],
                        'chef': ['ERROR', 'User authentication failure']
                            }

            except Exception as ex:
                    errormessage = DinnerMenuItem('Today', 'Process Options Error', 'O365', ex)
                    print("app_menu.getEditOptions() Process Options Error", ex)
                    return {
                        'dt': int(time.time()),
                        'option': [],
                        'chef': ['ERROR']
                            }
        else:
            # Return not a lot as not enabled
            return {
                'dt': int(time.time()),
                'option': [],
                'chef': []
                    }


    def getRecipeOptions(self, siteid=0, menudata=None):
        """
        Get Recipe data from OneNote.
        Fires off php script to get data

        :param siteid: Site ID
        :type siteid: int
        :param menudata: Menu Data to get recipes for
        :type menudata: dictionary
        """
        if siteid != 0 and menudata != None:
            for menudataitem in menudata:
                if (menudataitem and 'recipeurl' in menudataitem and '.one%7C' in menudataitem['recipeurl'] and 'sharepoint' in menudataitem['recipeurl']):
                    base64_bytes = base64.b64encode(menudataitem['recipeurl'].encode("utf-8"))
                    base64_string = base64_bytes.decode("utf-8")
                    os.system('php -f alternate/eDataMenuRecipe.php ' + siteid + ' ' + str(menudataitem['rid']) + ' ' + base64_string)


    def savedata(self, filename, jsondata):
        """
        Save json Infomation into specified file.
        
        :param filename: menu or options with site id
        :type filename: string
        :param jsondata: Json Information
        :type jsondata: dictionary
        """

        try:
            with open(self.datapath + str(filename) + '.json', 'w') as fp:
                json.dump(jsondata, fp)

        except Exception as ex:
            print('ERROR:app_menu.savedata('+filename+')', ex)


    def putNewItem(self, siteconfig=None, menuitem=None):
        """
        Will Put a new Menu item into excel

        :param siteconfig: Site Config Data
        :type siteconfig: dictionary
        :param menuitem: Menu Item Data
        :type menuitem: DinnerMenuItem
        :return: true if good
        :rtype: bool
        """
        # Check have config and enabled
        if siteconfig != None and menuitem != None and siteconfig['refresh'] != 0:
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
                    returndata = {'dt': int(time.time())}

                    # Connect to Storage Drive, and get file
                    if self._json_config['plaintext'] == False:
                        o365_storagedrive = o365_account.storage().get_drive(helpcrypto().decode(siteconfig['driveid']))
                        o365_storagedrivefile = o365_storagedrive.get_item(helpcrypto().decode(siteconfig['itemid']))
                    else:
                        o365_storagedrive = o365_account.storage().get_drive(siteconfig['driveid'])
                        o365_storagedrivefile = o365_storagedrive.get_item(siteconfig['itemid'])
                    returndata['modified'] = o365_storagedrivefile.modified.strftime("%a %d %b, %H:%M")
                    returndata['modifiedby'] = str(o365_storagedrivefile.modified_by)

                    # Open Excel File, and worksheet
                    o365_excelfile = WorkBook(o365_storagedrivefile, persist=True)
                    o365_excelfilews = o365_excelfile.get_worksheet(siteconfig['sheetname'])

                    # Save changes
                    datacella = o365_excelfilews.get_range('A' + str(menuitem.rowindex))
                    datacellb = o365_excelfilews.get_range('B' + str(menuitem.rowindex))
                    datacellc = o365_excelfilews.get_range('C' + str(menuitem.rowindex))
                    datacelld = o365_excelfilews.get_range('D' + str(menuitem.rowindex))
                    if datacella:
                        menuitem.datetext = str(datacella.text[0][0])
                        datacellb.values = menuitem.dinneroption
                        datacellc.values = menuitem.chef
                        datacelld.values = menuitem.ingredients
                        datacellb.update()
                        datacellc.update()
                        datacelld.update()
                        o365_excelfile.session.close_session()
                        return True
                    else:
                        return False
                else:
                    # Return not a lot as not authenticated
                    errormessage = DinnerMenuItem('Today', 'User authentication failure', 'O365-MENU')
                    print (errormessage.getobj())
                    return False

            except Exception as ex:
                    errormessage = DinnerMenuItem('Today', 'putNewItem Error', 'O365-MENU', ex)
                    print (errormessage.getobj())
                    return False
        else:
            # Return not a lot as not enabled
            return False


    def notifyNewItem(self, siteconfig=None, menuitem=None):
        """
        Notify Teams of menu Change

        :param siteconfig: Site Config Data
        :type siteconfig: dictionary
        :param menuitem: Menu Item Data
        :type menuitem: DinnerMenuItem
        :return: true if good
        :rtype: bool
        """
        # Check have config and enabled
        if siteconfig != None and menuitem != None and siteconfig['refresh'] != 0 and 'teams-webhookurl' in siteconfig:
            try:
                posturl = siteconfig['teams-webhookurl']
                postheaders = {'Content-Type': 'application/json'}

                content = "<div>" +\
                            "<h3>" + menuitem.datetext + "</h3>" +\
                            "<b>Option:</b> " + menuitem.dinneroption + "<br/>" +\
                            "<b>Chef:</b> " + menuitem.chef + "<br/>" +\
                            "<b>Ingredients:</b> " + menuitem.ingredients + "</div>"
                postpayload = { "text": content}

                teamresponse = requests.post(posturl, headers=postheaders, data=json.dumps(postpayload))
                # print(teamresponse.text.encode('utf8'))
                return True

            except Exception as ex:
                    errormessage = DinnerMenuItem('Today', 'notifyNewItem Error', 'O365-MENU', ex)
                    print (errormessage.getobj())
                    return False
        else:
            # Return not a lot as not enabled
            return False



class DinnerMenuItem():
    """ Single Dinner Menu Item """

    def __init__(self, datetext='', dinneroption='', chef='', ingredients='', notes='', today=False):
        self.datetext = str(datetext)
        self.dinneroption = str(dinneroption)
        self.chef = str(chef)
        self.ingredients = str(ingredients)
        self.notes = str(notes)
        self.today = bool(today)
        self.rowindex = 0

    def __str__(self):
        return '{}: {} by {} [{}]'.format(self.datetext, self.dinneroption, self.chef, self.ingredients)

    def readrow(self, excelrow):
        """ 
        Read single row from excel range

        :param excelrow: Excel Row Range
        :type excelrow: O365.excel.Range
        """
        if excelrow:
            self.datetext = str(excelrow.text[0][0])
            self.dinneroption = str(excelrow.text[0][1])
            self.chef = str(excelrow.text[0][2])
            self.ingredients = str(excelrow.text[0][3])
            self.notes = str(excelrow.text[0][4])
            self.rowindex = excelrow.row_index + 1


    def readrows(self, excelrow, rownum):
        """ 
        Read specific row from multi-row excel range

        :param excelrow: Excel Row Range
        :type excelrow: O365.excel.Range
        :param rownum: Row number to read
        :type rownum: int
        """
        if excelrow:
            self.datetext = str(excelrow.text[rownum][0])
            self.dinneroption = str(excelrow.text[rownum][1])
            self.chef = str(excelrow.text[rownum][2])
            self.ingredients = str(excelrow.text[rownum][3])
            self.notes = str(excelrow.text[rownum][4])
            self.rowindex = excelrow.row_index + rownum + 1


    def getobj(self):
        # self.dinneroption = self.__formatHtml(self.dinneroption)
        self.chef = self.__formatHtml(self.chef)
        # self.ingredients = self.__formatHtml(self.ingredients)

        return {
                "rid": self.rowindex,
                "day": self.datetext,
                "meal": self.dinneroption,
                "chef": self.chef,
                "ingredients": self.ingredients,
                "today": self.today
            }


    def __formatHtml(self, invalue):
        """ Format string to be HTML safe """
        invalue = invalue.replace("&", "&amp;")
        invalue = invalue.replace("<", "&lt;")
        invalue = invalue.replace(">", "&gt;")
        invalue = invalue.replace('"', "&quot;")
        invalue = invalue.replace("'", "&apos;")
        return invalue



class DinnerOptionItem():
    """ Single Dinner Option Item """

    def __init__(self, dinneroption='', ingredients='', cooktime='', recipeurl=''):
        self.dinneroption = str(dinneroption)
        self.ingredients = str(ingredients)
        self.cooktime = str(cooktime)
        self.recipeurl = str(recipeurl)
        self.rowindex = 0

    def __str__(self):
        return '{}: {} [{}]'.format(self.dinneroption, self.ingredients, self.cooktime)

    def readrow(self, excelrow):
        if excelrow:
            self.dinneroption = str(excelrow.text[0][0])
            self.ingredients = str(excelrow.text[0][1])
            self.cooktime = str(excelrow.text[0][2])
            self.recipeurl = str(excelrow.text[0][3])
            self.rowindex = excelrow.row_index + 1

    def readrows(self, excelrow, rownum):
        if excelrow:
            self.dinneroption = str(excelrow.text[rownum][0])
            self.ingredients = str(excelrow.text[rownum][1])
            self.cooktime = str(excelrow.text[rownum][2])
            self.recipeurl = str(excelrow.text[rownum][3])
            self.rowindex = excelrow.row_index + rownum + 1

    def getobj(self):
        # self.dinneroption = self.__formatHtml(self.dinneroption)
        # self.ingredients = self.__formatHtml(self.ingredients)
        # self.recipeurl = self.__formatHtml(self.recipeurl)

        return {
                "rid": self.rowindex,
                "option": self.dinneroption,
                "ingredients": self.ingredients,
                "cooktime": self.cooktime,
                "recipeurl": self.recipeurl
            }

    def __formatHtml(self, invalue):
        invalue = invalue.replace("&", "&amp;")
        invalue = invalue.replace("<", "&lt;")
        invalue = invalue.replace(">", "&gt;")
        invalue = invalue.replace('"', "&quot;")
        invalue = invalue.replace("'", "&apos;")
        return invalue
