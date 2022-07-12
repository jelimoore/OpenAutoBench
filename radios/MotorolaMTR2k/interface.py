from builtins import ConnectionError
import warnings
import logging
import time
import serial
from radios.MotorolaRSSRepeater.interface import MotorolaRSSRepeater

class MotorolaQuantar(MotorolaRSSRepeater):
    def __init__(self, serialPort, baud=9600):
        super().__init__(serialPort, baud=baud)

    def connect(self):
        try:
            super().connect()
            self.getVersion()
            self.serialNumber = self.get('STN SN')
            self.codeplugVersion = self.get('CP VER')
            self.getHardware()

            self._logger.debug("Serial: {}".format(self.serialNumber))
            self._logger.debug("Firmware: {}".format(self.firmwareVersion))
            self._logger.debug("Codeplug: {}".format(self.codeplugVersion))
            self._logger.debug("Hardware: {}".format(self.hardware))

            connected = True
        except Exception as e:
            self._logger.debug(e)
            raise Exception("Failure connecting to radio")

    def getVersion(self):
        self.firmwareVersion = self.get('FW_VER SC')
        #self.firmwareVersions['Exciter'] = self.get('FW_VER EX')
        #self.firmwareVersions['Wireline'] = self.get('FW_VER WL')
        #self.firmwareVersions['Boot1'] = self.get('FW_VER BOOT.O')
        #self.firmwareVersions['Boot2'] = self.get('FW_VER BOOT2.O')

    def getHardware(self):
        self.hardware += 'RX: {}, '.format(self.get('HW_VER RX'))
        self.hardware += 'PA: {}, '.format(self.get('HW_VER PA'))
        self.hardware += 'TX: {}, '.format(self.get('HW_VER TX'))
        self.hardware += 'Wireline: {}, '.format(self.get('HW_VER WL'))
        self.hardware += 'Option Board 1: {}, '.format(self.get('HW_VER OP1'))
        self.hardware += 'Option Board 2: {} '.format(self.get('HW_VER OP2'))