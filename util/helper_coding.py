import base64
import socket
from Crypto.Cipher import AES

class helper_coding():
    """
    Text Encryption functionality.

    Locked to local machine, by hostname and CPU Serial.

    Examples
    --------
    from helper_coding import helper_coding

    helper_coding().encode('Hello World!')

    helper_coding().decode('pfe3nZDWVVSupVtL')
    """
    def __init__(self):
        pass

    def __getSerial(self):
        """
        Extract serial from cpuinfo file

        :return: CPU Serial Number
        :rtype: string
        """
        cpuserial = "0000000000000000"
        try:
            gsfile = open('/proc/cpuinfo', 'r')
            for line in gsfile:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            gsfile.close()
        except:
            cpuserial = "ERROR000000000"
        return str.encode(cpuserial.zfill(16))


    def __getHostname(self):
        """
        Get machine hostname, padded to 16 characters
        :return: Padded Hostname
        :rtype: string
        """
        return str.encode(socket.gethostname().zfill(16))


    def decode(self, stringin):
        """
        Decode string.
        Takes a BASE64 encapsulated, machine encoded string, and returns plain text

        :param stringin: BASE64 encapsulated, machine encoded string
        :type stringin: string
        :return: Plain Text
        :rtype: string
        """
        cipherobj = AES.new(self.__getHostname(), AES.MODE_CFB, self.__getSerial())
        return cipherobj.decrypt(base64.b64decode(str.encode(stringin))).decode('UTF-8')


    def encode(self, stringin):
        """
        Encode string.
        Takes a plain text and machine encodes, then BASE64 encapsulated

        :param stringin: Plain Text
        :type stringin: string
        :return: BASE64 encapsulated, machine encoded string
        :rtype: string
        """
        cipherobj = AES.new(self.__getHostname(), AES.MODE_CFB, self.__getSerial())
        return base64.b64encode(cipherobj.encrypt(str.encode(stringin))).decode('UTF-8')
