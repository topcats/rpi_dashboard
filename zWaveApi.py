import urllib2
import urllib
import httplib
import base64
import json
import time
import socket

class zWaveApi(object):

    zlogin_cookie = ''
    zlogin_username = ''
    zlogin_password = ''
    zlogin_apibaseURL = 'http://localhost:8083/ZAutomation/api/v1/'
    zlogin_server = ''
    zlogin_serverpath = ''

    def __init__(self, zUsername, zPassword, zBaseUrl):
        self.zlogin_username = zUsername
        self.zlogin_password = zPassword
        self.zlogin_apibaseURL = zBaseUrl
        self.strServer = self.zlogin_apibaseURL.replace('http://', '')
        self.strServer = self.strServer[:self.strServer.index('/')]
        self.strServerPath = self.zlogin_apibaseURL.replace('http://'+self.strServer,'')

    def DoLogin(self):
        post_login = urllib.urlencode({'form': 'true', 'login': self.zlogin_username, 'password': self.zlogin_password, 'keepme': 'false', 'default_ui': 1})

        webheaders = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
        webconn = httplib.HTTPConnection(self.strServer)
        webconn.request("POST", self.strServerPath+'login', post_login, webheaders)
        webresponse = webconn.getresponse()
        webresponseCookie = webresponse.getheader('set-cookie')#['ZWAYSession']
        webresponseCookie = webresponseCookie.replace(' ','')
        webresponseCookie = webresponseCookie[webresponseCookie.index('ZWAYSession='):].replace('ZWAYSession=','')
        webresponseCookie = webresponseCookie[:webresponseCookie.index(';')]
        self.zlogin_cookie = webresponseCookie
        #webdata = webresponse.read()
        webconn.close()
        return webresponse.status


    def getDevices(self):
        #Double check login
        if (self.zlogin_cookie == ''):
            self.DoLogin()

        webheaders = {'Content-type': 'application/json', "Accept": "application/json", "Cookie": "ZWAYSession="+self.zlogin_cookie}
        webconn = httplib.HTTPConnection(self.strServer)
        webconn.request("GET", self.strServerPath+'devices?since=0', '', webheaders)
        webresponse = webconn.getresponse()
        webdata = webresponse.read()
        webconn.close()
        json_obj = json.loads(webdata)
        return json_obj['data']['devices']


    def setDeviceCommand(self, deviceid, newcommand):
        #switchMultilevel on / off / min / max / exact?level=40 / increase / decrease / update
        #switchBinary on / off / update
        #toggleButton on

        #Double check login
        if (self.zlogin_cookie == ''):
            self.DoLogin()

        #Check inputs
        if (deviceid == ''):
            return 0
        if (newcommand == ''):
            return 0

        #Do Command
        webheaders = {'Content-type': 'application/json', "Accept": "application/json", "Cookie": "ZWAYSession="+self.zlogin_cookie}
        webconn = httplib.HTTPConnection(self.strServer)
        webconn.request("GET", self.strServerPath+'devices/'+deviceid+'/command/'+newcommand, '', webheaders)
        webresponse = webconn.getresponse()
        webdata = webresponse.read()
        webconn.close()

        #Check Response
        json_obj = json.loads(webdata)
        if (json_obj['code'] == 200):
            return 1
        else:
            return 0

