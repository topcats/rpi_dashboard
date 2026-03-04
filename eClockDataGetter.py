#!/usr/bin/python3
# rpi_dashboard
# =================
# Data Getter - 15 Minute runner

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

import os
import shutil
import glob
import json
import time
import datetime as dt


# MAKE SURE WE is in the correct directory
os.chdir('/home/pi/dashdisplay')


def fnGetLastUpdated(datafile, refreshdefault):
    """ Determine Last Updated from Json file
    :param datafile: Datafile to check
    :param refreshdefault: Default refresh interval
    """
    data_timediff = int(refreshdefault)*61
    try:
        if os.path.isfile(datafile+'.json'):
            with open(datafile+'.json') as fp:
                json_obj = json.load(fp)
            data_timediff = int(time.time()) - int(json_obj['dt'])
    except Exception as ex:
        print("fnGetLastUpdated("+datafile+") WARN: No Source Current)", ex)
        data_timediff = int(refreshdefault)*61
    return data_timediff/60



def fnGetWeather():
    """ Get Weather Information """

    from infosource.app_weather import app_weather

    # Open Config
    with open('conf/weather.json') as fp:
        json_config = json.load(fp)

    if int(json_config['refresh']) == 0:
        # Clear all Downloaded Data and Icon Files
        for filePath in glob.glob(app_weather.datapath + 'current_*.json'):
            try:
                os.remove(filePath)
            except:
                print("fnGetWeather(Error while deleting file)", filePath)
        for filePath in glob.glob(app_weather.datapath + 'forecast_*.json'):
            try:
                os.remove(filePath)
            except:
                print("fnGetWeather(Error while deleting file)", filePath)
        for filePath in glob.glob(app_weather.datapath + 'icon_*.png'):
            try:
                os.remove(filePath)
            except:
                print("fnGetWeather(Error while deleting file)", filePath)

    else:
        weatheraction = app_weather(config=json_config)
        # Loop round all locations and get data
        for weatherlocation in json_config["locations"]:
            data_timediff = fnGetLastUpdated(app_weather.datapath + 'current_' + str(weatherlocation['townid']), json_config['refresh'])
            if data_timediff >= int(json_config['refresh']):
                # Get Weather, check for name and get icon image

                # - Current
                json_obj = weatheraction.getcurrent(weatherlocation['townid'])
                weatheraction.savedata('current_' + str(weatherlocation['townid']), json_obj)

                # - Current Icon
                iconpath = weatheraction.downloadicon(json_obj['weather'][0]['icon'])
                if weatherlocation['townid'] == 2650311 and iconpath is not None and os.path.isfile(iconpath):
                    shutil.copyfile(iconpath, app_weather.datapath + 'icon_weather.png')

                # - Forecast
                json_obj = weatheraction.getforecast(weatherlocation['townid'])
                weatheraction.savedata('forecast_' + str(weatherlocation['townid']), json_obj)

                # - Get Active Weather Icons
                for i in range(0, 20):
                    iconpath = weatheraction.downloadicon(json_obj['list'][i]['weather'][0]['icon'])
                    if weatherlocation['townid'] == 2650311 and iconpath is not None and os.path.isfile(iconpath) and i < 5:
                        shutil.copyfile(iconpath, app_weather.datapath + 'icon_forecast' + str(i+1) + '.png')

            else:
                print("fnGetWeather("+str(weatherlocation['townid'])+") Info: Not needed")


def fnGetTide():
    """ Get Tide Information """

    from infosource.app_tide import app_tide

    # Open Config
    with open('conf/tide.json') as fp:
        json_config = json.load(fp)

    if int(json_config['refresh']) == 0:
        # Clear all Downloaded Data and Icon Files
        for filePath in glob.glob(app_tide.datapath + '*.json'):
            try:
                os.remove(filePath)
            except:
                print("fnGetTide(Error while deleting file)", filePath)

    else:
        # Loop round all locations and get data
        tideaction = app_tide(config=json_config)
        for tidelocation in json_config["locations"]:
            data_timediff = fnGetLastUpdated(app_tide.datapath + str(tidelocation['portid']), json_config['refresh'])
            if data_timediff >= int(json_config['refresh']):
                # Get Forecast
                json_obj = tideaction.getforecast(tidelocation['portid'])
                json_obj['dt'] = int(time.time())
                # Save Info
                tideaction.savedata(tidelocation['portid'], json_obj)
            else:
                print("fnGetTide("+tidelocation['portid']+") Info: Not needed")


def fnGetDlna():
    """ Get DLNA Information """
    # No longer Used

    from infosource.app_dlna import app_dlna
    _data_file = 'data/dlna_stats.json'
    _data_fileold = 'data/dlna_stats.old.json'

    # Open Config
    with open('conf/dlna.json') as fp:
        json_config = json.load(fp)

    # Load Existing
    try:
        with open(_data_file) as fp:
            json_data = json.load(fp)
        data_timediff = int(time.time()) - int(json_data['updated'])
    except:
        json_data = {"audio": 0, "video": 0, "updated": 0}
        data_timediff = int(json_config['refresh'])*61
    if not 'audio' in json_data:
        json_data['audio'] = 0
    if not 'video' in json_data:
        json_data['video'] = 0
    if not 'photo' in json_data:
        json_data['photo'] = 0

    if int(json_config['refresh']) == 0 or int(json_config['type']) == 0:
        # Turn off update (delete data)
        if os.path.isfile(_data_file):
            os.remove(_data_file)
        if os.path.isfile(_data_fileold):
            os.remove(_data_fileold)
    elif data_timediff >= (int(json_config['refresh'])*60):
        # Get Data
        dataresponse = app_dlna(config=json_config).process()
        if int(json_data['audio']) != int(dataresponse['audio']) or int(json_data['video']) != int(dataresponse['video']) or int(json_data['photo']) != int(dataresponse['photo']):
            if os.path.isfile(_data_file):
                shutil.copyfile(_data_file, _data_fileold)
            with open(_data_file, 'w') as outs:
                json.dump(dataresponse, outs)
        else:
            print("fnGetDlna(): No Change")
    else:
        print("fnGetDlna(): Not needed")


def fnGetO365Calendar():
    """ Get Office365 Calendar information """
    # VERY OLD NOT IN USE

    from infosource.app_calendar import app_calendar

    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)

    data_timediff = fnGetLastUpdated('data/o365_calendar.json', json_config['schedule']['refresh'])
    if data_timediff >= int(json_config['schedule']['refresh']):
        # Get Data
        o365action = app_calendar(config=json_config)
        with open('data/o365_calendar.json', 'w') as outs:
            json.dump(o365action.process('schedule'), outs)
    else:
        print("fnGetO365Calendar(): Not needed")


def fnGet0365CalendarHP():
    """
    Get Office365 Calendar information
    
    NB: Uses PHP!!
    """

    print("fnGet0365CalendarHP():")
    os.system('php -f alternate/eClockDataGetterTC.php')


def fnGetO365InfoPane():
    """ Get Office365 Info Pane Calendar information """

    from infosource.app_calendar import app_calendar

    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)
    with open('conf/site.json') as fp:
        json_siteconfig = json.load(fp)

    # Loop round all site locations and get data
    o365action = app_calendar(config=json_config)
    for json_site in json_siteconfig["locations"]:
        time.sleep(1)
        if json_site is None:
            json_site = {}
        if not 'calendar' in json_site:
            json_site['calendar'] = {}
        if json_site['calendar'] is None:
            json_site['calendar'] = {}
            json_site['calendar']['refresh'] = 0
        if not 'refresh' in json_site['calendar']:
            json_site['calendar']['refresh'] = 0
        if not 'manual' in json_site['calendar']:
            json_site['calendar']['manual'] = False

        data_timediff = fnGetLastUpdated(app_calendar.datapath+'infopane_'+str(json_site["id"]), json_site['calendar']['refresh'])
        if data_timediff >= int(json_site['calendar']['refresh']):
            # Get Data
            json_catsourcedata = {'MasterList':[]}
            if json_site['calendar']['manual']:
                # Manual process (from PHP lookup data)
                try:
                    # Manual Merge of Category List
                    json_catsourcedata = o365action.loaddata('infopane_'+str(json_site["id"])+'_cat')
                    o365action.set_categorylist(categorylist=json_catsourcedata['MasterList'])
                    # Manual Process ingest
                    json_sourcedata = o365action.loaddata('infopane_'+str(json_site["id"])+'s')
                    json_output = o365action.processmanual(siteconfig=json_site['calendar'], sourcedata=json_sourcedata['value'])
                    o365action.savedata('infopane_'+str(json_site["id"]), json_output)
                except Exception as ex:
                    print('Calendar Source file issue. '+str(json_site["id"]), ex)
            else:
                # Automatic process
                json_output = o365action.process(siteconfig=json_site['calendar'])
                o365action.savedata('infopane_'+str(json_site["id"]), json_output)


def fnGetO365Menu():
    '''Get Office365 Info Pane Dinner Menu information'''

    from infosource.app_menu import app_menu

    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)
    with open('conf/site.json') as fp:
        json_siteconfig = json.load(fp)

    # Loop round all site locations and get data
    o365action = app_menu(config=json_config)
    for json_site in json_siteconfig["locations"]:
        time.sleep(1)
        if json_site is None:
            json_site = {}
        if not 'menu' in json_site:
            json_site['menu'] = {}
        if json_site['menu'] is None:
            json_site['menu'] = {}
            json_site['menu']['refresh'] = 0
        if not 'refresh' in json_site['menu']:
            json_site['menu']['refresh'] = 0
        if not 'allowedit' in json_site['menu']:
            json_site['menu']['allowedit'] = False

        data_timediff = fnGetLastUpdated(app_menu.datapath+'menu_'+str(json_site["id"]), json_site['menu']['refresh'])
        if data_timediff >= int(json_site['menu']['refresh']):
            # Get Data
            json_menu = o365action.process(siteconfig=json_site['menu'])
            o365action.savedata('menu_'+json_site["id"], json_menu)
            # Get Options Data
            json_menuoptions = o365action.getEditOptions(siteconfig=json_site['menu'])
            o365action.savedata('options_'+json_site["id"], json_menuoptions)
            o365action.getRecipeOptions(json_site["id"], json_menuoptions['option'])
        else:
            print("fnGetO365Menu("+str(json_site['id'])+") Info: Not needed")


def fnGetO365Task():
    """Get Office365 Info Pane Tasks information"""

    from infosource.app_tasks import app_tasks

    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)
    with open('conf/site.json') as fp:
        json_siteconfig = json.load(fp)

    # Loop round all site locations and get data
    o365action = app_tasks(config=json_config)
    for json_site in json_siteconfig["locations"]:
        time.sleep(1)
        if json_site is None:
            json_site = {}
        if not 'tasks' in json_site:
            json_site['tasks'] = {}
        if json_site['tasks'] is None:
            json_site['tasks'] = {}
            json_site['tasks']['refresh'] = 0
        if not 'refresh' in json_site['tasks']:
            json_site['tasks']['refresh'] = 0
        if not 'manual' in json_site['tasks']:
            json_site['tasks']['manual'] = False

        data_timediff = fnGetLastUpdated('data/o365_tasks_'+str(json_site["id"]), json_site['tasks']['refresh'])
        if data_timediff >= int(json_site['tasks']['refresh']):
            # Get Data
            if json_site['tasks']['manual']:
                try:
                    with open('data/o365_tasks_'+json_site["id"]+'s.json') as fp:
                        json_sourcedata = json.load(fp)
                    json_output = o365action.processmanual(siteconfig=json_site['tasks'], sourcedata=json_sourcedata['value'])
                    with open('data/o365_tasks_'+json_site["id"]+'.json', 'w') as outs:
                        json.dump(json_output, outs)
                except Exception as ex:
                    print('Tasks Source file issue. '+json_site["id"], ex)
            else:
                json_output = o365action.process(siteconfig=json_site['tasks'])
                with open('data/o365_tasks_'+json_site["id"]+'.json', 'w') as outs:
                    json.dump(json_output, outs)
        else:
            print("fnGetO365Task("+str(json_site['id'])+") Info: Not needed")


def fnGetO365Photo():
    """ Get Office365 Photo Collage """

    from infosource.app_photo import app_photo

    # Open Config
    with open('conf/o365.json') as fp:
        json_config = json.load(fp)
    with open('conf/site.json') as fp:
        json_siteconfig = json.load(fp)

    o365action = app_photo(config=json_config)
    for json_site in json_siteconfig["locations"]:
        time.sleep(1)
        if json_site is None:
            json_site = {}
        if not 'photo' in json_site:
            json_site['photo'] = {}
        if json_site['photo'] is None:
            json_site['photo'] = {}
            json_site['photo']['refresh'] = 0
        if not 'refresh' in json_site['photo']:
            json_site['photo']['refresh'] = 0

        data_timediff = fnGetLastUpdated('data/photo/photo_'+str(json_site["id"]), json_site['photo']['refresh'])
        if data_timediff >= int(json_site['photo']['refresh']):
            # Get Data
            o365datajson = o365action.process(siteconfig=json_site['photo'], locationid=json_site["id"])
            o365datajson['imagecollage'] = []
            o365datajson['imagecollagevirt'] = []

            if o365datajson['imagecount'] == 12:
                o365action.makeCollage(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder0name'], inputs={'photo_'+json_site["id"]+'_0.jpg','photo_'+json_site["id"]+'_1.jpg','photo_'+json_site["id"]+'_2.jpg'}, outputfile='image_'+json_site["id"]+'_0.png')
                o365action.makeCollage(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder1name'], inputs={'photo_'+json_site["id"]+'_3.jpg','photo_'+json_site["id"]+'_4.jpg','photo_'+json_site["id"]+'_5.jpg'}, outputfile='image_'+json_site["id"]+'_1.png')
                o365action.makeCollage(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder2name'], inputs={'photo_'+json_site["id"]+'_6.jpg','photo_'+json_site["id"]+'_7.jpg','photo_'+json_site["id"]+'_8.jpg'}, outputfile='image_'+json_site["id"]+'_2.png')
                o365action.makeCollage(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder3name'], inputs={'photo_'+json_site["id"]+'_9.jpg','photo_'+json_site["id"]+'_10.jpg','photo_'+json_site["id"]+'_11.jpg'}, outputfile='image_'+json_site["id"]+'_3.png')
                o365datajson['imagecollage'] = ['image_'+json_site["id"]+'_0.png', 'image_'+json_site["id"]+'_1.png', 'image_'+json_site["id"]+'_2.png', 'image_'+json_site["id"]+'_3.png']
                if 'v' in json_site['photo']:
                    o365action.makeCollageVirt(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder0name'], inputs={'photo_'+json_site["id"]+'_0.jpg','photo_'+json_site["id"]+'_1.jpg','photo_'+json_site["id"]+'_2.jpg'}, outputfile='image_'+json_site["id"]+'_v0.png')
                    o365action.makeCollageVirt(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder1name'], inputs={'photo_'+json_site["id"]+'_3.jpg','photo_'+json_site["id"]+'_4.jpg','photo_'+json_site["id"]+'_5.jpg'}, outputfile='image_'+json_site["id"]+'_v1.png')
                    o365action.makeCollageVirt(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder2name'], inputs={'photo_'+json_site["id"]+'_6.jpg','photo_'+json_site["id"]+'_7.jpg','photo_'+json_site["id"]+'_8.jpg'}, outputfile='image_'+json_site["id"]+'_v2.png')
                    o365action.makeCollageVirt(siteconfig=json_site['photo'], locationid=json_site["id"], title=o365datajson['folder3name'], inputs={'photo_'+json_site["id"]+'_9.jpg','photo_'+json_site["id"]+'_10.jpg','photo_'+json_site["id"]+'_11.jpg'}, outputfile='image_'+json_site["id"]+'_v3.png')
                    o365datajson['imagecollagevirt'] = ['image_'+json_site["id"]+'_v0.png', 'image_'+json_site["id"]+'_v1.png', 'image_'+json_site["id"]+'_v2.png', 'image_'+json_site["id"]+'_v3.png']
            o365action.savedata('photo_'+str(json_site["id"]), o365datajson)
        else:
            print("fnGetO365Photo("+str(json_site['id'])+") Info: Not needed")




#######################################
# Main program
fnGetWeather()
fnGetTide()
# fnGetDlna()
# fnGetO365Calendar()
fnGet0365CalendarHP()
fnGetO365InfoPane()
fnGetO365Menu()
# fnGetO365Task()
fnGetO365Photo()
