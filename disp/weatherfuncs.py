# rpi_dashboard
# =================
# Display Function: Weather Data
# - disp_weatherfuncs : GetCurrent, GetForecast

import json
import os
import datetime


class disp_weatherfuncs:
    """ Display Lib: Weather Functions """

    __datapath = None
    townid = None
    """ Weather Town ID """

    def __init__(self, datapath, townid):
        """
        Initialize Weather Display Functions

        :param datapath: Path to Weather Data
        :type datapath: string
        :param townid: Town ID for Weather Data
        :type townid: int
        """
        self.__datapath = datapath
        self.townid = townid
        pass


    def __getParentSelectorFromObjecta(self, obj, value, key):
        for k, v in obj.items():
            if value >= v[key][0] and value < v[key][1]:
                return k


    def __GetWindSpeedDesc(self, value):
        """
        Get Wind Speed Description from speed value

        :param value: Wind Speed Value
        :type value: float
        :return: Wind Speed Description
        :rtype: string
        """

        try:
            dataFile = os.path.normpath(os.path.join(self.__datapath, 'wind-speed-data.json'))
            with open(dataFile) as fp:
                json_obj = json.load(fp)
            return self.__getParentSelectorFromObjecta(json_obj['en'], float(value), "speed_interval")
        except Exception as ex:
            print("ERROR:eDisplay.disp_weatherfuncs.__GetWindSpeedDesc()", ex)


    def GetCurrent(self):
        """
        Load Weather Data from File

        :return: Weather Data
        :rtype: dict
        """
        # Get Current Weather Data
        try:
            currentFile = os.path.normpath(os.path.join(self.__datapath, 'current_'+str(self.townid)+'.json'))
            current_wind = ""
            with open(currentFile) as fp:
                json_obj = json.load(fp)

            current_desc = (json_obj['weather'][0]['description']).title()
            if 'wind' in json_obj and 'speed' in json_obj['wind']:
                current_wind = self.__GetWindSpeedDesc(json_obj['wind']['speed'])
            current_temp = "{:.1f}".format(json_obj['main']['temp'])
            current_time = datetime.datetime.fromtimestamp(int(json_obj['dt'])).strftime('%H:%M')
            current_location = json_obj['name']
            current_icon = json_obj['weather'][0]['icon']
            current_sunlight = datetime.datetime.fromtimestamp(int(json_obj['sys']['sunrise'])).strftime('%H:%M')
            current_sunlight = current_sunlight + ' - '
            current_sunlight = current_sunlight + datetime.datetime.fromtimestamp(int(json_obj['sys']['sunset'])).strftime('%H:%M')
        except Exception as ex:
            print("ERROR:eDisplay.disp_weatherfuncs.GetCurrent()", ex)

        # Return Weather Data
        weatherdata = {
            'description': current_desc,
            'wind': current_wind,
            'temperature': current_temp,
            'time': current_time,
            'location': current_location,
            'icon': current_icon,
            'sunlight': current_sunlight
        }
        return weatherdata


    def GetForecast(self):
        """
        Load Weather Data from File

        :return: Weather Data
        :rtype: dict
        """
        # Get Forecast Weather Data
        try:
            forecastFile = os.path.normpath(os.path.join(self.__datapath, 'forecast_'+str(self.townid)+'.json'))
            with open(forecastFile) as fp:
                json_obj = json.load(fp)

            weatherdata = []
            for i in range(0, 5):
                forecast_time = datetime.datetime.fromtimestamp(int(json_obj['list'][i]['dt'])).strftime('%H:%M')
                forecast_desc = (json_obj['list'][i]['weather'][0]['description']).title()
                if 'wind' in json_obj['list'][i] and 'speed' in json_obj['list'][i]['wind']:
                    forecast_wind = self.__GetWindSpeedDesc(json_obj['list'][i]['wind']['speed'])
                else:
                    forecast_wind = ""
                forecast_icon = json_obj['list'][i]['weather'][0]['icon']
                forecast_temp = "{:.1f}".format(json_obj['list'][i]['main']['temp'])

                weatherdata.append({
                    'time': forecast_time,
                    'description': forecast_desc,
                    'wind': forecast_wind,
                    'temperature': forecast_temp,
                    'icon': forecast_icon
                })

        except Exception as ex:
            print("ERROR:eDisplay.disp_weatherfuncs.GetForecast()", ex)

        # Return Weather Data
        return weatherdata
