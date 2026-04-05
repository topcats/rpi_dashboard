# rpi_dashboard
# =================
# Data Source - O365 Photo Reader
# - app_photo: Photo Reader and collage maker

from O365 import Account, FileSystemTokenBackend
from util.helper_coding import helper_coding as helpcrypto
import json
import time
from datetime import date, datetime as dt
import random
from PIL import Image, ImageDraw, ImageFont, ExifTags
from pi_heif import register_heif_opener

register_heif_opener()

class app_photo():
    """ Application Lib, will connect to O365 and obtain the a photo college """

    datapath = 'data/photo/'
    _tokenpath = 'data/'
    _tokenfilename = 'o365_token.json'

    _imagewidth = 1186
    _imageheight = 606
    _imagescale = 0.8

    _grabcollage = 4
    _grabimages = 3

    def __init__(self, config=None):
        """ Photo grabber

        :param config: O365 Configuration object
        """
        self._json_config = config

        #Set Config Defaults
        if self._json_config is None:
            self._json_config = {}
        if not 'plaintext' in self._json_config:
            self._json_config['plaintext'] = False


    def process(self, siteconfig=None, locationid=None):
        """ Will Get the Photos data and format read for saving.
        :return: Saves Json of Images
        """
        # Check have config and enabled
        if siteconfig is None:
            siteconfig = {}
        if not 'refresh' in siteconfig:
            siteconfig['refresh'] = 0
        if siteconfig['refresh'] != 0:

            try:
                # Connect to O365 (O365 Account Logon)
                o365_tokenbackend = FileSystemTokenBackend(token_path=self._tokenpath, token_filename=self._tokenfilename)
                if self._json_config['plaintext'] == False:
                    o365_credentials = (helpcrypto().decode(self._json_config['client_id']), helpcrypto().decode(self._json_config['client_secret']))
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=helpcrypto().decode(self._json_config['tenant_id']), token_backend=o365_tokenbackend)
                else:
                    o365_credentials = (self._json_config['client_id'], self._json_config['client_secret'])
                    o365_account = Account(o365_credentials, auth_flow_type='credentials', tenant_id=self._json_config['tenant_id'], token_backend=o365_tokenbackend)

                if not o365_account.is_authenticated:  # will check if there is a token and has not expired
                    o365_account.authenticate()

                if o365_account.is_authenticated:
                    returndata = {'dt': int(time.time())}

                    # Get root Photos folder
                    o365_storagedrive = o365_account.storage().get_drive(siteconfig['driveid'])
                    o365_storagedriveroot = o365_storagedrive.get_item(siteconfig['rootid'])
                    photofolders = []
                    for item in o365_storagedriveroot.get_child_folders():
                        photofolders.append({'name': item.name, 'id': item.object_id})
                    returndata['foldercount'] = len(photofolders)
                    # print(returndata['foldercount'])

                    # Find this cycle base
                    outputcount = 0
                    outputid = []
                    while outputcount < self._grabcollage:
                        # Find Random Folder, but no duplictes
                        photofolder = photofolders[random.randrange(start=15, stop=returndata['foldercount'])]
                        while self.folderfind(outputid, photofolder['id']):
                            photofolder = photofolders[random.randrange(start=0, stop=returndata['foldercount'])]

                        # Get all photos in folder including sub folders
                        o365_storagedrivephoto = o365_storagedrive.get_item(photofolder['id'])
                        photoItems = []
                        for item in o365_storagedrivephoto.get_items():
                            if item.is_folder:
                                for subitem in item.get_items():
                                    if subitem.is_photo or subitem.is_image:
                                        if subitem.name.lower().endswith('.jpg') or subitem.name.lower().endswith('.jpeg') or item.name.lower().endswith('.heic'):
                                            photoItems.append({'name': subitem.name, 'id': subitem.object_id})
                            elif item.is_file:
                                if item.is_photo or item.is_image:
                                    if item.name.lower().endswith('.jpg') or item.name.lower().endswith('.jpeg') or item.name.lower().endswith('.heic'):
                                        photoItems.append({'name': item.name, 'id': item.object_id})

                        # only add if has photos in folder
                        if len(photoItems) >= 3:
                            returndata['folder'+str(outputcount)+'name'] = photofolder['name']
                            returndata['folder'+str(outputcount)+'id'] = photofolder['id']
                            returndata['image'+str(outputcount)+'count'] = len(photoItems)
                            returndata['images'+str(outputcount)] = photoItems
                            outputcount = outputcount + 1
                            outputid.append(photofolder['id'])

                    # loop folders and download images
                    returndata['images'] = []
                    imagenum = 0
                    for ci in range(self._grabcollage):
                        # Loop Folders
                        iImageCount = self._grabimages
                        if returndata['image'+str(ci)+'count'] < iImageCount:
                            iImageCount = returndata['image'+str(ci)+'count']

                        for ii in range(iImageCount):
                            # Download images from folder (without duplicates)
                            photoItem = returndata['images'+str(ci)][random.randrange(start=0, stop=returndata['image'+str(ci)+'count'])]
                            while self.photofind(returndata['images'], photoItem['id']):
                                photoItem = returndata['images'+str(ci)][random.randrange(start=0, stop=returndata['image'+str(ci)+'count'])]
                            returndata['images'].append({'num': imagenum, 'name': photoItem['name'], 'id': photoItem['id']})
                            o365_photoItem = o365_storagedrive.get_item(photoItem['id'])
                            o365_photoItem.download(to_path=self.datapath, name="photo_"+str(locationid)+"_"+str(imagenum)+o365_photoItem.extension.lower())

                            # Check if image conversion needed
                            if o365_photoItem.extension.lower() == '.heic':
                                im = Image.open(self.datapath + "photo_"+str(locationid)+"_"+str(imagenum)+o365_photoItem.extension.lower())
                                im.save(self.datapath + "photo_"+str(locationid)+"_"+str(imagenum)+'.jpg')

                            imagenum = imagenum + 1
                            time.sleep(1)

                        returndata['images'+str(ci)] = []

                    returndata['imagecount'] = len(returndata['images'])
                    return returndata

                else:
                    # Return not a lot as not authenticated
                    return {
                        'dt': int(time.time()),
                        'foldercount':0,
                        'foldername':'User authentication failure',
                        'folderid':'',
                        'imagecount':0,
                        'images':[]
                            }

            except Exception as ex:
                return {
                    'dt': int(time.time()),
                    'foldercount':0,
                    'foldername':'Process Error:' + str(ex),
                    'folderid':'',
                    'imagecount':0,
                    'images':[]
                        }
        else:
            # Return not a lot as not enabled
            return {
                'dt': int(time.time()),
                'foldercount':0,
                'foldername':'',
                'folderid':'',
                'imagecount':0,
                'images':[]
                    }


    def makeCollage(self, siteconfig=None, locationid=None, title=None, inputs=None, outputfile=None):
        if siteconfig is None:
            siteconfig = {}
        if not 'h' in siteconfig:
            siteconfig['h'] = {}
        if not 'width' in siteconfig['h']:
            siteconfig['h']['width'] = self._imagewidth
        if not 'height' in siteconfig['h']:
            siteconfig['h']['height'] = self._imageheight

        im  = Image.new(mode="RGBA", size=(siteconfig['h']['width'], siteconfig['h']['height']))

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break

        # Loop Inputs
        if inputs != None:
            if len(inputs) >= 4:
                self._imagescale = 0.6
            elif len(inputs) >= 3:
                self._imagescale = 0.7
            else:
                self._imagescale = 0.8

            imagecounter = 0
            for item in inputs:
                ImageAlt = Image.open(self.datapath + item)
                try:
                    ImageAltExif = ImageAlt._getexif()
                    if (ImageAltExif and ImageAltExif[orientation]):
                        if ImageAltExif[orientation] == 3:
                            ImageAlt=ImageAlt.rotate(180, expand=True)
                        elif ImageAltExif[orientation] == 6:
                            ImageAlt=ImageAlt.rotate(270, expand=True)
                        elif ImageAltExif[orientation] == 8:
                            ImageAlt=ImageAlt.rotate(90, expand=True)
                except Exception as ex:
                    print('Photo Exif Error:' + str(ex))
                maxWidth = int(siteconfig['h']['width'] * self._imagescale)
                maxHeight = int(ImageAlt.height / (ImageAlt.width / maxWidth))
                if maxHeight > int(siteconfig['h']['height'] * self._imagescale):
                    maxHeight = int(siteconfig['h']['height'] * self._imagescale)
                    maxWidth = int(ImageAlt.width / (ImageAlt.height / maxHeight))
                ImageAlt = ImageAlt.resize((maxWidth, maxHeight))
                if imagecounter == 3:
                    im.paste(ImageAlt, (10,int(siteconfig['h']['height'] - ImageAlt.height)))
                elif imagecounter == 2:
                    if len(inputs) >= 4:
                        im.paste(ImageAlt, (int(siteconfig['h']['width'] - ImageAlt.width),int(siteconfig['h']['height'] - ImageAlt.height)))
                    else:
                        im.paste(ImageAlt, (int((siteconfig['h']['width'] - ImageAlt.width)/2),int(siteconfig['h']['height'] - ImageAlt.height)))
                elif imagecounter == 1:
                    if len(inputs) == 2:
                        im.paste(ImageAlt, (int(siteconfig['h']['width'] - ImageAlt.width),int(siteconfig['h']['height'] - ImageAlt.height)))
                    else:
                        im.paste(ImageAlt, (int(siteconfig['h']['width'] - (ImageAlt.width+10)),0))
                else:
                    im.paste(ImageAlt, (0,0))
                imagecounter = imagecounter + 1

        # Add Title
        if title != None:
            imNameFont = ImageFont.truetype('FreeSans.ttf', size=32)
            imName = ImageDraw.Draw(im)
            imName.text((12,siteconfig['h']['height']-38), title, font=imNameFont, fill=(255,255,255))
            imName.text((10,siteconfig['h']['height']-40), title, font=imNameFont, fill=(0,0,0))

        #Save Output
        if outputfile != None:
            im.save(self.datapath + outputfile)


    def makeCollageVirt(self, siteconfig=None, locationid=None, title=None, inputs=None, outputfile=None):
        if siteconfig is None:
            siteconfig = {}
        if not 'v' in siteconfig:
            siteconfig['v'] = {}
        if not 'width' in siteconfig['v']:
            siteconfig['v']['width'] = self._imageheight
        if not 'height' in siteconfig['v']:
            siteconfig['v']['height'] = self._imagewidth

        im  = Image.new(mode="RGBA", size=(siteconfig['v']['width'], siteconfig['v']['height']))

        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break

        # Loop Inputs
        if inputs != None:
            if len(inputs) >= 4:
                self._imagescale = 0.62
            elif len(inputs) >= 3:
                self._imagescale = 0.72
            else:
                self._imagescale = 0.8

            imagecounter = 0
            for item in inputs:
                # Open Image
                ImageAlt = Image.open(self.datapath + item)

                # Rotate if needed
                try:
                    ImageAltExif = ImageAlt._getexif()
                    if (ImageAltExif and ImageAltExif[orientation]):
                        if ImageAltExif[orientation] == 3:
                            ImageAlt=ImageAlt.rotate(180, expand=True)
                        elif ImageAltExif[orientation] == 6:
                            ImageAlt=ImageAlt.rotate(270, expand=True)
                        elif ImageAltExif[orientation] == 8:
                            ImageAlt=ImageAlt.rotate(90, expand=True)
                except Exception as ex:
                    print('Photo Exif Error:' + str(ex))

                # Grab image details and resize
                maxWidth = int(siteconfig['v']['width'] * self._imagescale)
                maxHeight = int(ImageAlt.height / (ImageAlt.width / maxWidth))
                if maxHeight > int(siteconfig['v']['height'] * self._imagescale):
                    maxHeight = int(siteconfig['v']['height'] * self._imagescale)
                    maxWidth = int(ImageAlt.width / (ImageAlt.height / maxHeight))
                ImageAlt = ImageAlt.resize((maxWidth, maxHeight))

                # Place Image
                if imagecounter == 3:
                    # bottom, right
                    im.paste(ImageAlt, (int(siteconfig['v']['width']-ImageAlt.width),int(siteconfig['v']['height']-ImageAlt.height)))
                elif imagecounter == 2:
                    if len(inputs) >= 4:
                        # lower middle, left
                        im.paste(ImageAlt, (0,int(siteconfig['v']['height']/2)))
                    else:
                        # bottom, middle
                        im.paste(ImageAlt, (int((siteconfig['v']['width']-ImageAlt.width)/2),int(siteconfig['v']['height']-ImageAlt.height)))
                elif imagecounter == 1:
                    if len(inputs) == 2:
                        # bottom, right
                        im.paste(ImageAlt, (int(siteconfig['v']['width']-ImageAlt.width),int(siteconfig['v']['height']-ImageAlt.height)))
                    elif len(inputs) == 3:
                        # top middle lower, right
                        im.paste(ImageAlt, (int(siteconfig['v']['width']-ImageAlt.width),int(siteconfig['v']['height']/1.5-ImageAlt.height)))
                    else:
                        # top middle, right
                        im.paste(ImageAlt, (int(siteconfig['v']['width']-ImageAlt.width),int(siteconfig['v']['height']/2-ImageAlt.height)))
                else:
                    # top, left
                    im.paste(ImageAlt, (0,0))
                imagecounter = imagecounter + 1

        # Add Title
        if title != None:
            imNameFont = ImageFont.truetype('FreeSans.ttf', size=32)
            imName = ImageDraw.Draw(im)
            imName.text((12,siteconfig['v']['height']-38), title, font=imNameFont, fill=(255,255,255))
            imName.text((10,siteconfig['v']['height']-40), title, font=imNameFont, fill=(0,0,0))

        # Save Output
        if outputfile != None:
            im.save(self.datapath + outputfile)


    def photofind(self, arr, id):
        """ Checks the array to match if the ID exists
        :return: true if found else false
        :rtype: bool """
        for x in arr:
            if x["id"] == id:
                return True
        return False


    def folderfind(self, arr, id):
        """ Check if id is in the list
        :return: true if found else false
        :rtype: bool """
        for x in arr:
            if x == id:
                return True
        return False


    def savedata(self, filename, jsondata):
        """ Save json Infomation
        :param filename: with site id
        :param jsondata: Json Information
        """

        try:
            with open(self.datapath + str(filename) + '.json', 'w', encoding='utf-8') as fp:
                json.dump(jsondata, fp)

        except Exception as ex:
            print('ERROR:app_photo.savedata('+filename+')', ex)
