# rpi_dashboard
# =================
# Display Function: Weather Data
# - disp_weatherfuncs : GetCurrent, GetForecast

import json
import os
import datetime


class disp_weatherfuncs:
    """ Display Lib: Weather Functions """

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


    def GetCurrent(self):
        """
        Load Weather Data from File

        :return: Weather Data
        :rtype: dict
        """
        # Get Current Weather Data
        try:
            currentFile = os.path.normpath(os.path.join(self.__datapath, 'current_'+str(self.townid)+'.json'))

            with open(currentFile) as fp:
                json_obj = json.load(fp)

            current_desc = (json_obj['weather'][0]['description']).title()
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
                forecast_icon = json_obj['list'][i]['weather'][0]['icon']
                forecast_temp = "{:.1f}".format(json_obj['list'][i]['main']['temp'])

                weatherdata.append({
                    'time': forecast_time,
                    'description': forecast_desc,
                    'temperature': forecast_temp,
                    'icon': forecast_icon
                })

        except Exception as ex:
            print("ERROR:eDisplay.disp_weatherfuncs.GetForecast()", ex)

        # Return Weather Data
        return weatherdata
