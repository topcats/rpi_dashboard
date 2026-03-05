# rpi_dashboard
# =================
# Data Source - Mini DLNA or Serviio Media Counter
# - app_dlna:

import json
import time
import urllib.request

class app_dlna():
    """ Application Lib, will connect to various DLNA server and obtain data """

    def __init__(self, config=None):
        """ DLNA Stats grabber

        :param config: Configuration object
        """
        self._json_config = config

    def process(self):
        """ Get DLNA Information.
        :return: Returns the full menu
        :rtype: dictionary
        """

        vreturn = {
            "updated": int(time.time()),
            "url": str(self._json_config['url'])
            }

        if self._json_config['type'] == 2:
            # Serviio
            datalookup = self.__fnGetDlnaServiio()

        elif self._json_config['type'] == 1:
            # MiniDLNA
            datalookup = self.__fnGetDlnaMini()

        else:
            datalookup = {
                'audio': 0,
                'video': 0,
                'photo': 0
                }

        # return response
        vreturn["audio"] = datalookup['audio']
        vreturn["video"] = datalookup['video']
        vreturn["photo"] = datalookup['photo']
        return vreturn


    def __fnGetDlnaMini(self):
        """Get miniDLNA Information"""

        try:
            #url_to_call = 'http://'+url+':8200/'
            response = urllib.request.urlopen(self._json_config['url'])
            response_data = response.read()
            count_video = response_data.index("Video")
            count_videoe = response_data.index('</tr>', count_video)
            value_video = response_data[count_video:count_videoe]
            value_video = value_video.replace('Video files</td><td>', '')
            value_video = value_video.replace('</td>', '')
            count_audio = response_data.index("Audio")
            count_audioe = response_data.index('</tr>', count_audio)
            value_audio = response_data[count_audio:count_audioe]
            value_audio = value_audio.replace('Audio files</td><td>', '')
            value_audio = value_audio.replace('</td>', '')

            return {
                'audio': value_audio,
                'video': value_video,
                'photo': None
                }

        except Exception as ex:
            print('Error:app_dlna.fnGetDlnaMini()', ex)
            return None


    def __fnGetDlnaServiio(self):
        """Get Serviiio DLNA Information"""

        try:
            #wurl_to_call = 'http://'+config.get('DLNA', 'url')+':23423/rest/library-status'
            wrequestheaders = {'Accept': 'application/json'}
            wrequest = urllib.request.Request(self._json_config['url'], headers=wrequestheaders)
            wresponse = urllib.request.urlopen(wrequest).read().decode('utf-8')
            if not wresponse:
                raise Exception("No Response")
            json_obj = json.loads(wresponse)

            return {
                'audio': int(json_obj['totalAudioFiles']),
                'video': int(json_obj['totalVideoFiles']),
                'photo': int(json_obj['totalImageFiles'])
                }

        except Exception as ex:
            print('Error:app_dlna.fnGetDlnaServiio()', ex)
            return None
