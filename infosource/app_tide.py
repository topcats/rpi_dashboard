# rpi_dashboard
# =================
# Data Source - Tides Reader
# - app_tide: Read from UK EasyTide data

import json
import time
import urllib.request
from datetime import date, datetime as dt
import os

class app_tide():
    """ Application Lib: Tides, will connect to easytide.admiralty.co.uk and obtain 7 day data """
    
    datapath = 'data/weather/tide_'
    
    def __init__(self, config=None):
        """ Tides Forecast grabber

        :param config: Tide Configuration object
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'refresh' in self._json_config:
            self._json_config['refresh'] = 0


    def getforecast(self, portid = "0000"):
        """ Get Tides Forecast Infomation from Admiralty EasyTide
        :param portid: Port ID Number, should be 4 numbers
        :rtype: dictionary
        """

        try:
            time.sleep(1)
            wurl_to_call = 'https://easytide.admiralty.co.uk/Home/GetPredictionData?stationId=' + str(portid)
            wrequestheaders = {'Accept': 'application/json'}
            wrequest = urllib.request.Request(wurl_to_call, headers=wrequestheaders)
            wresponse = urllib.request.urlopen(wrequest).read().decode('utf-8')
            if not wresponse:
                raise Exception("No Response")
            json_obj = json.loads(wresponse)

            if not 'dt' in json_obj:
                json_obj['dt'] = int(time.time())

            return json_obj

        except Exception as ex:
            print('Error:app_tide.getforecast()', ex)
            return None


    def savedata(self, portid, jsondata):
        """ Save Tide Forecast Infomation
        :param portid: Port ID Number, should be 4 numbers
        :param jsondata: Tide Json Information
        """

        try:
            with open(self.datapath + str(portid) + '.json', 'w') as fp:
                json.dump(jsondata, fp)

        except Exception as ex:
            print('Error:app_tide.savedata()', ex)
