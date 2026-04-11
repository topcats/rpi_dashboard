# rpi_dashboard
# =================
# Display Function: Menu Data
# - MenuItem : Data item
# - disp_menufuncs : GetToday

import json
import os
from datetime import datetime, timedelta
from disp.screens.ui import colours
from infosource.app_menu import DinnerMenuItem



class MenuItem(DinnerMenuItem):
    """
    Menu Item for Display
    """
    pass

    def __init__(self, menuitem = None):
        """
        LoadMenuItem

        :param menuitem: Source Menu Data
        :type menuitem: dict
        """

        if menuitem is not None:
            self.datetext = str(menuitem['day'])
            self.dinneroption = str(menuitem['meal'])
            self.chef = str(menuitem['chef'])
            self.ingredients = str(menuitem['ingredients'])
            self.today = bool(menuitem['today'])
        pass


    def GetText(self):
        """
        Return Text for Menu Item

        :return: option and chef
        :rtype: string
        """
        return "            🍽\t" + self.dinneroption + " by " + self.chef



class disp_menufuncs:
    """ Display Lib: Menu Functions """

    def __init__(self, datapath, locationid):
        """
        Initialize Menu Display Functions

        :param datapath: Path to Menu Data
        :type datapath: string
        :param locationid: Location ID for Site Data
        :type locationid: int
        """
        self.datapath = datapath
        self.locationid = locationid
        pass


    def getToday(self):
        """
        Load Menu Data from File
        Finds the item with the "today" flag set to True, and returns that as a MenuItem object
        
        :return: Menu Data
        :rtype: dict
        """
        menuitem = []
        try:
            currentFile = os.path.normpath(os.path.join(self.datapath, 'menu_'+str(self.locationid)+'.json'))
            with open(currentFile, encoding='utf-8') as fp:
                json_obj = json.load(fp)

            for o365_menu in json_obj['menu']:
                item = MenuItem(o365_menu)
                if (item.today):
                    menuitem.append(item)
                    break

        except Exception as ex:
            print("ERROR:eDisplay.disp_menufuncs.getToday()", ex)

        # Return Data, even if blank
        return menuitem


    def getTomorrow(self):
        """
        Load Menu Data from File
        Finds the item after the one with the "today" flag set to True, and returns that as a MenuItem object
        
        :return: Menu Data
        :rtype: dict
        """
        menuitem = []
        try:
            currentFile = os.path.normpath(os.path.join(self.datapath, 'menu_'+str(self.locationid)+'.json'))
            with open(currentFile, encoding='utf-8') as fp:
                json_obj = json.load(fp)

            foundToday = False
            for o365_menu in json_obj['menu']:
                item = MenuItem(o365_menu)
                if foundToday:
                    menuitem.append(item)
                    break
                if (item.today):
                    foundToday = True
                    continue

        except Exception as ex:
            print("ERROR:eDisplay.disp_menufuncs.getTomorrow()", ex)

        # Return Data, even if blank
        return menuitem