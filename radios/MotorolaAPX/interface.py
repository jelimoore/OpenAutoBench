from builtins import ConnectionError
import numpy as np
import warnings
import socket
import threading
import logging
import time
from radios.MotorolaCommon import MotorolaIP
import socket
from enum import Enum

class MotorolaAPX(MotorolaIP):
    FREON_MODELS = ['H92', 'H91']
    class RADIOBAND(Enum):
        BAND_VHF = 0x00
        BAND_UHF1 = 0x01
        BAND_UHF2 = 0x02
        BAND_7800 = 0x03
        BAND_900_1 = 0x04
        BAND_900_2 = 0x05

    RF_TEST_FREQUENCIES = {}
    RF_TEST_FREQUENCIES['VHF'] = {}
    RF_TEST_FREQUENCIES['UHF1'] = {}
    RF_TEST_FREQUENCIES['UHF2'] = {}
    RF_TEST_FREQUENCIES['7-800'] = {}

    RF_TEST_FREQUENCIES['VHF']['RX'] = []
    RF_TEST_FREQUENCIES['VHF']['TX'] = []

    RF_TEST_FREQUENCIES['UHF1']['RX'] = []
    RF_TEST_FREQUENCIES['UHF1']['TX'] = []

    RF_TEST_FREQUENCIES['UHF2']['RX'] = []
    RF_TEST_FREQUENCIES['UHF2']['TX'] = []

    RF_TEST_FREQUENCIES['7-800']['RX'] = []
    RF_TEST_FREQUENCIES['7-800']['TX'] = []


    def __init__(self, ipAddress='192.168.128.1'):
        self.connected = False
        self._ipAddress = ipAddress
        self._port = 8002
        self.modelNumber = ''
        self.serialNumber = ''
        self.codeplugVersion = ''
        self.firmwareVersion = ''
        self.tuningVersion = ''
        self.bootloaderVersion = ''
        self.dspVersion = ''
        self.secureVersion = ''
        self.secureAlgs = ''
        self.bands = []
        self.isFreon = False
        self.isRepeater = False
        self.formFactor = ''
        self.powerLevel = ''
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self._socket.connect((self._ipAddress, self._port))
            self.modelNumber = self.getModelNumber()
            self.serialNumber = self.getSerialNumber()
            self.firmwareVersion = self.getFirmwareVersion()
            #self.codeplugVersion = self.getCodeplugVersion()
            # this errors out, we'll figure it out later
            #self.tuningVersion = self.getTuningVersion()
            self.dspVersion = self.getDspVersion()
            self.secureVersion = self.getSecureVersion()
            self.secureAlgs = self.getSecureAlgorithms()

            self.bandsplit = self.modelNumber[3:4]
            self.powerLevel = self.modelNumber[4:5]
            self.formFactor = self.modelNumber[0:1]
            
            
            self._logger.debug("Model: {}".format(self.modelNumber))
            self._logger.debug("Serial: {}".format(self.serialNumber))
            self._logger.debug("Firmware: {}".format(self.firmwareVersion))
            self._logger.debug("DSP: {}".format(self.dspVersion))
            self._logger.debug("Codeplug: {}".format(self.codeplugVersion))
            self._logger.debug("Tuning: {}".format(self.tuningVersion))
            self._logger.debug("Bootloader: {}".format(self.bootloaderVersion))
            self._logger.debug("Secure: {}".format(self.secureVersion))
            self._logger.debug("Algs: {}".format(self.secureAlgs))
            self._logger.debug("Bandsplit: {}".format(self.bandsplit))
            self._logger.debug("Power Level: {}".format(self.powerLevel))
            self._logger.debug("Form Factor: {}".format(self.formFactor))

            if (self.modelNumber[0:3] in MotorolaAPX.FREON_MODELS):
                self.isFreon = True
            
            self._logger.debug("Freon: {}".format(self.isFreon))

            connected = True
        except Exception as e:
            self._logger.debug(e)
            raise Exception("Failure connecting to radio")

    def disconnect(self):
        self._socket.close()
    
    def send(self, bytesIn):
        txOpcode = bytesIn[0:2]
        payloadLen = len(bytesIn).to_bytes(2, "big")
        self._socket.send(payloadLen + bytesIn)

        t_end = time.time() + 5
        while time.time() < t_end:
            try:
                data = self._socket.recv(1024)
                #print("Got {}".format(data))
                rxOpcode = data[2:4]
                packet = data[2:]
                # check for reply opcode
                if(rxOpcode[0] | 0x80 == 0x80):
                    # received response
                    # this is sort of cursed, and i intend to fix this
                    # basically convert the bytes to int, subtract 0x8000, and turn it back to bytes
                    # then we can compare to see if we got the transmitted opcode back
                    rxOpcode = int.from_bytes(rxOpcode, "big")
                    rxOpcode -= 0x8000
                    rxOpcode = rxOpcode.to_bytes(2, "big")
                if (txOpcode == rxOpcode):
                    return packet[2:]
            except Exception as e:
                self._logger.error("Remote side dropped")
                self._logger.debug(e)

    def getSoftpotFreqs(self, softpotId):
        idBytes = softpotId.to_bytes(1, "big")
        result = self.send(b'\x00\x01\x08' + idBytes)
        freqString = result[3:]
        # each frequency is represented by 4 bytes
        numFreqs = int(len(freqString) / 4)
        freqList = []
        for i in range(0,numFreqs):
            freq = freqString[i*4:i*4+4]
            freq = (int.from_bytes(freq, "big") * 5) / 1000000
            freqList.append(freq)
        return freqList
