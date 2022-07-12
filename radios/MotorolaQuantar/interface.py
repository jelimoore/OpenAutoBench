from builtins import ConnectionError
import warnings
import logging
import time
import serial
from radios.MotorolaRSSRepeater.interface import MotorolaRSSRepeater

class MotorolaQuantar(MotorolaRSSRepeater):
    def __init__(self, serialPort, baud=9600):
        super().__init__(serialPort, baud)
        self.firmwareVersions = {}
    
    def send(self, commandIn):
        self._serialPort.reset_input_buffer()
        packet = commandIn.encode() + b'\n'
        #print("Sending {}".format(packet))
        self._serialPort.write(packet)

        # flush one line to clear the echoed line (what you send comes back)
        echoLine = self._serialPort.readline()
        #print("Read {}".format(echoLine))
        line = self._serialPort.readline()
        #print("Read {}".format(line))
        line = line.replace(b'\r', b'')
        line = line.replace(b'\n', b'')
        line = line.decode()
        if (line.startswith('?')):
            raise Exception("Repeater returned error: {}".format(line))
        return line

    def connect(self):
        try:
            super().connect()
            self.getVersion()
            self.stationName = self.get('STN NAME')
            self.serialNumber = self.get('STN SN')
            self.codeplugVersion = self.get('CP VER')
            self.rx1Band = self.get('RX FREQ_BAND')
            self.rx2Band = self.get('RX2 FREQ_BAND')
            self.txBand = self.get('TX FREQ_BAND')
            self.hardwareVersion = self.get('HW_VER')
            self.getHardware()

            self._logger.debug("Station Name: {}".format(self.stationName))
            self._logger.debug("Serial: {}".format(self.serialNumber))
            self._logger.debug("Firmware: {}".format(self.firmwareVersions))
            self._logger.debug("Codeplug: {}".format(self.codeplugVersion))
            self._logger.debug("Hardware: {}".format(self.hardware))
            self._logger.debug("RX Band: {}".format(self.rx1Band))
            self._logger.debug("RX 2 Band: {}".format(self.rx2Band))
            self._logger.debug("TX Band: {}".format(self.txBand))
            self._logger.debug("Hardware Version: {}".format(self.hardwareVersion))

            connected = True
        except Exception as e:
            self._logger.debug(e)
            raise Exception("Failure connecting to radio")

    def getVersion(self):
        self.firmwareVersions['Control'] = self.get('FW_VER SC')
        self.firmwareVersions['Exciter'] = self.get('FW_VER EX')
        self.firmwareVersions['Wireline'] = self.get('FW_VER WL')
        self.firmwareVersions['Boot1'] = self.get('FW_VER BOOT.O')
        self.firmwareVersions['Boot2'] = self.get('FW_VER BOOT2.O')

    def getHardware(self):
        self.hardware += 'RX: {}, '.format(self.get('RX TYPE'))
        self.hardware += 'PA: {}, '.format(self.get('PA TYPE'))
        self.txPower = self.get('PA ORD_PWR')
        self.hardware += 'PA Power: {}, '.format(self.txPower)
        self.hardware += 'TX: {}, '.format(self.get('TX COMPA'))
        self.hardware += 'Wireline: {}, '.format(self.get('WL PORT_STAT'))
        self.hardware += 'Power: {}, '.format(self.get('PS RATED_PWR'))
        self.hardware += 'Battery: {} '.format(self.get('PS BATT_TYPE'))