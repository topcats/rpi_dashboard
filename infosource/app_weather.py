# rpi_dashboard
# =================
# Data Source - Weather from OpenWeatherMap
# - app_weather: Grab Current and Forecast data

from util.helper_coding import helper_coding as helpcrypto
import json
import time
import urllib.request
from datetime import date, datetime as dt
import os

class app_weather():
    """ Application Lib:Weather, will connect to OpenWeatherMap and obtain the Current and Forecast data """

    datapath = 'data/weather/'

    _baseurl= 'http://api.openweathermap.org/data/2.5/'

    def __init__(self, config=None):
        """ Weather Current and forecast grabber

        :param config: Weather Configuration object
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'refresh' in self._json_config:
            self._json_config['refresh'] = 0
        if not 'refreshicon' in self._json_config:
            self._json_config['refreshicon'] = 30
        if not 'plaintext' in self._json_config:
            self._json_config['plaintext'] = False


    def getcurrent(self, townid = 0):
        """ Get Current Weather Infomation from OpenWeatherMap
        :param townid: OpenWeatherMap Town ID
        :rtype: dictionary
        """

        try:
            time.sleep(1)
            wurl_to_call = self._baseurl + 'weather?id=' + str(townid) + '&units=metric'
            if self._json_config['plaintext'] == False:
                wurl_to_call = wurl_to_call + '&appid=' + str(helpcrypto().decode(self._json_config['openweather_appid']))
            else:
                wurl_to_call = wurl_to_call + '&appid=' + str(self._json_config['openweather_appid'])
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
            print('Error:app_weather.getcurrent()', ex)
            return None


    def getforecast(self, townid = 0):
        """ Get Forecast Weather Infomation from OpenWeatherMap
        :param townid: OpenWeatherMap Town ID
        :rtype: dictionary
        """

        try:
            time.sleep(1)
            wurl_to_call = self._baseurl + 'forecast?id=' + str(townid) + '&units=metric'
            if self._json_config['plaintext'] == False:
                wurl_to_call = wurl_to_call + '&appid=' + str(helpcrypto().decode(self._json_config['openweather_appid']))
            else:
                wurl_to_call = wurl_to_call + '&appid=' + str(self._json_config['openweather_appid'])
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
            print('Error:app_weather.getforecast()', ex)
            return None


    def downloadicon(self, iconcode):
        """ Downloads and save Weather Icon image file
        :param iconcode: OpenWeatherMap IconCode
        """
        try:
            time.sleep(1.5)
            iconpath = self.datapath + 'icon_' + str(iconcode) + '.png'

            # Only download image if not local
            if not os.path.isfile(iconpath) or (int(time.time()) - int(os.path.getctime(iconpath))) >= (int(self._json_config['refreshicon'])*86400):
                weatherimage_url = 'http://openweathermap.org/img/wn/' + str(iconcode) + '@2x.png'
                urllib.request.urlretrieve(weatherimage_url, iconpath)
                time.sleep(0.5)
            else:
                print("app_weather.downloadicon(" + iconcode + "): Not needed")
            return iconpath

        except Exception as ex:
            print('Error:app_weather.fnGetWeatherIcon()', ex)
            return None


    def savedata(self, filename, jsondata):
        """ Save json Infomation
        :param filename: current or forecast with town id
        :param jsondata: Weather Json Information
        """

        try:
            with open(self.datapath + str(filename) + '.json', 'w', encoding='utf-8') as fp:
                json.dump(jsondata, fp)

        except Exception as ex:
            print('Error:app_weather.savedata('+filename+')', ex)
