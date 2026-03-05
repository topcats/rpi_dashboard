# rpi_dashboard
# =================
# Display Function: Config Control
# - load
# - save

import json
import os

class disp_conf:
    """ Display Lib: Configuration Functions """

    __defaultconfig = { "zwave": {"enabled": False} }

    def __init__(self, configfile):
        """ Initialize Configuration Functions """
        self.__configfile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'+configfile))
        pass


    def loadConfig(self):
        """
        Load Configuration from JSON file

        :return: Configuration Dictionary
        :rtype: dict
        """
        try:
            with open(self.__configfile, 'r') as fp:
                config = json.load(fp)
            return config
        except Exception as ex:
            print("ERROR:eDisplay.disp_conf.loadConfig()", ex)
            return self.__defaultconfig


    def saveConfig(self, config):
        """
        Save Configuration to JSON file

        :param config: Configuration Dictionary
        :type config: dict
        """
        try:
            with open(self.__configfile, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as ex:
            print("ERROR:eDisplay.disp_conf.saveConfig()", ex)
            pass
