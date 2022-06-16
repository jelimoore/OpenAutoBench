import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxReferenceOscillator(AutoTest):
    name = "Tx - Reference Oscillator"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequency = None
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.bandsplit == "Q" or
            self._radio.bandsplit == "T"):
            return True
        else:
            return False

    def setup(self):
        self._instrument._sendCmd("DISP RFAN")
        if (self._radio.bandsplit == "Q"):
            self._frequency = 469.975
        if (self._radio.bandsplit == "T"):
            self._frequency = 511.825
        if (self._radio.bandsplit == "R"):
            self._frequency = 477.425

    def performTest(self):
        self._logger.info("Beginning reference oscillator test")
        self._radio.setPowerLevel(3)
        self._radio.send(b'\x00\x02\x10')
        # set frequency 00 0b 05 9a 3f f8 64 01
        self._radio.setTXFrequency(self._frequency)
        self._instrument.setRXFrequency(self._frequency * 1000000)
        self._radio.keyRadio()
        time.sleep(4)
        err = round(self._instrument.measureRFError(self._frequency * 1000000), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = ''
        if (self._radio.isGen2):
            absFreq = float((self._frequency * 1000000) - err)
            logLine = "Absolute frequency: {}hz".format(absFreq)
            
        else:
            logLine = "Measured Frequency Error: {}hz".format(err)
        
        self._logger.info(logLine)
        self.report = logLine + '\n'
    def tearDown(self):
        pass
