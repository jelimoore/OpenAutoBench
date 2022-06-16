import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxModBalance():
    name = "Tx - Modulation Balance"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.formFactor == 'M'):
            if (self._radio.bandsplit == "Q" and self._radio.powerLevel == "P"):
                return True
            else:
                return False
        else:
            return False
    def setup(self):
        self._instrument.setDisplay("AFAN")
        self._instrument._sendCmd("AFAN:FILT1 '<20Hz HPF'")
        self._instrument._sendCmd("AFAN:FILT2 '15kHz LPF'")

        if (self._radio.isGen2):
            # UHF R1
            if (self._radio.bandsplit == "Q"):
                self._frequencies =[403.000,
                                    410.000,
                                    420.000,
                                    430.500,
                                    440.000,
                                    450.000,
                                    460.000,
                                    470.000]
        else:
            # UHF R1
            if (self._radio.bandsplit == "Q"):
                self._frequencies =[403.000,
                                    412.000,
                                    426.000,
                                    436.500,
                                    437.000,
                                    449.000,
                                    458.000,
                                    470.000]

            # UHF R2
            if (self._radio.bandsplit == "T"):
                self._frequencies =[450.000,
                                    474.000,
                                    490.000,
                                    492.000,
                                    498.000,
                                    503.000,
                                    512.000]

        # Unified UHF (Gen2 portables)
        if (self._radio.bandsplit == "R"):
            self._frequencies =[403.000,
                                423.000,
                                445.000,
                                470.000,
                                470.000005,
                                496.000,
                                527.000,
                                460.000005]
        
    def performTest(self):
        self._logger.info("Beginning Mod Balance test")
        self._radio.setPowerLevel(3)

        for freq in self._frequencies:
            self._logger.info("Testing Frequency {}".format(freq))
            self._radio.setTXFrequency(freq, lastByte=b'\x00')
            self._instrument.setRXFrequency(freq * 1000000)
            # low tone
            self._radio.send(b'\x00\x02\x11')
            self._radio.keyRadio()
            time.sleep(5)
            lowdev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("Low tone: {}hz".format(lowdev))
            self._radio.unkeyRadio()
            time.sleep(1)

            # high tone
            self._radio.send(b'\x00\x02\x12')
            self._radio.keyRadio()
            time.sleep(5)
            highdev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("High Tone: {}hz".format(highdev))
            self._radio.unkeyRadio()
            time.sleep(1)

            self.report += 'Deviation at {}MHz: {}hz low tone, {}hz high tone\n'.format(freq, lowdev, highdev)
    def tearDown(self):
        pass
