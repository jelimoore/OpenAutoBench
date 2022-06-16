import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxReferenceOscillator(AutoTest):
    name = "Tx - Reference Oscillator"
    def __init__(self, radio, instrument, uplink=None, downlink=None):
        self._radio = radio
        self._instrument = instrument
        self._testPoints = []
        if (downlink is not None):
            self._testPoints = [downlink]
        else:
            self._testPoints = [140, 150, 440, 450, 460, 470, 900, 910, 920, 930]
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument._sendCmd("DISP RFAN")
        self._radio.setMode(interface.STATE_P25_CAL)
        #self._frequency = 450
    def performTest(self):
        #self._logger.info("Beginning reference oscillator test")
        for freq in self._testPoints:
            self._radio.setTXFrequency(freq)
            self._instrument.setRXFrequency(freq * 1000000)
            self._radio.keyRadio()
            time.sleep(5)
            err = round(self._instrument.measureRFError(freq * 1000000), 2)
            #print("Dekeying")
            self._radio.unkeyRadio()
            logLine = "Measured Frequency Error at {}MHz: {}hz".format(freq, err)
            self._logger.info(logLine)
            self.report += logLine + '\n'
            time.sleep(1)
    def tearDown(self):
        self._radio.setMode(interface.STATE_IDLE)
