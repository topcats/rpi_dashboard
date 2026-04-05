# rpi_dashboard
# =================
# Util System - O365 Config Mgmt
# - conf_o365: O365 Config Reader
#   - GetTenantID: Return O365 Tenant ID
#   - GetClientID: Return O365 Client ID
#   - GetClientSecret: Return O365 Client Secret

import os
import json
from util.helper_coding import helper_coding

class conf_o365():
    """ Application Helper: O365 Config Reader """

    __configfile = 'conf/o365.json'
    __defaultconfig = { "plaintext": True, "tenant_id": "", "client_id": "", "client_secret": "" }
    __config = None


    def __init__(self, configfile='conf/o365.json'):
        self.__configfile = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../'+configfile))
        pass


    def __LoadConfig(self):
        """
        Load O365 Configuration from JSON file

        Will load into local var, or set default if an error
        """
        if self.__config is None:
            try:
                with open(self.__configfile, 'r', encoding='utf-8') as fp:
                    self.__config = json.load(fp)
            except Exception as ex:
                print("ERROR:eDisplay.conf_o365.loadConfig()", ex)
                self.__config = self.__defaultconfig


    def GetTenantID(self):
        """
        Return O365 Tenant ID

        :return: Tenant ID
        :rtype: string
        """
        self.__LoadConfig()
        return str(self.__config['tenant_id'])


    def GetClientID(self):
        """
        Return O365 Client ID

        :return: Client ID
        :rtype: string
        """
        self.__LoadConfig()
        if self.__config['plaintext']:
            return str(self.__config['client_id'])
        else:
            decryptedpassword = helper_coding().decode(self.__config['client_id'])
            return decryptedpassword


    def GetClientSecret(self):
        """
        Return O365 Client Secret

        :return: Client Secret
        :rtype: string
        """
        self.__LoadConfig()
        if self.__config['plaintext']:
            return str(self.__config['client_secret'])
        else:
            decryptedpassword = helper_coding().decode(self.__config['client_secret'])
            return decryptedpassword
