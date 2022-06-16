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
        if (self._radio.isFreon):
            return True
        else:
            return False
    def setup(self):
        self._instrument.setDisplay("AFAN")
        self._instrument._sendCmd("AFAN:FILT1 '<20Hz HPF'")
        self._instrument._sendCmd("AFAN:FILT2 '15kHz LPF'")
        self._frequencies = self._radio.getSoftpotFreqs(0x02)

        
        
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

        self.report += '\n'
    def tearDown(self):
        pass
