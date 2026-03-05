# rpi_dashboard
# =================
# Display Function: Host Control
# - Set Brightness
# - Get Brightness
# - Screen On/Off
# - Check if Screen is On

class disp_rpifuncs:
    """ Display Lib: RPI Functions """

    __fileBrightness = '/sys/class/backlight/rpi_backlight/brightness'
    __filePower = '/sys/class/backlight/rpi_backlight/bl_power'

    def __init__(self):
        """ Initialize RPI Display Functions """
        pass


    def setBrightness(self, value):
        """
        Set RPI Screen Brightness
        The higher the value, the brighter the screen.

        :param value: Brightness level (1-255)
        :type value: int
        """
        try:
            rpibrightness = open(self.__fileBrightness, 'w')
            rpibrightness.write(str(value))
            rpibrightness.close()
        except Exception as ex:
            print("ERROR:eDisplay.disp_rpifunc.setBrightness()", ex)


    def getBrightness(self):
        """
        Get RPI Screen Brightness

        :return: Brightness level (1-255)
        :rtype: int
        """
        try:
            rpibrightness = open(self.__fileBrightness, 'r')
            value = int(rpibrightness.read())
            rpibrightness.close()
            return value
        except Exception as ex:
            print("ERROR:eDisplay.disp_rpifunc.getBrightness()", ex)
            return -1


    def screenOn(self):
        """
        Turn RPI Screen On
        """
        try:
            rpiscreen = open(self.__filePower, 'w')
            rpiscreen.write('0')
            rpiscreen.close()
        except Exception as ex:
            print("ERROR:eDisplay.disp_rpifunc.screenOn()", ex)


    def screenOff(self):
        """
        Turn RPI Screen Off
        """
        try:
            rpiscreen = open(self.__filePower, 'w')
            rpiscreen.write('1')
            rpiscreen.close()
        except Exception as ex:
            print("ERROR:eDisplay.disp_rpifunc.screenOff()", ex)


    def isScreenOn(self):
        """
        Check if RPI Screen is On

        :return: True if screen is on, False otherwise
        :rtype: bool
        """
        try:
            rpiscreen = open(self.__filePower, 'r')
            value = int(rpiscreen.read())
            rpiscreen.close()
            return value == 0
        except Exception as ex:
            print("ERROR:eDisplay.disp_rpifunc.isScreenOn()", ex)
            return False
