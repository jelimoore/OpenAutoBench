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
        if (self._radio.isFreon):
            return True
        if (self._radio.bandsplit == 'T'):
            return True
        
        return False

    def setup(self):
        self._instrument._sendCmd("DISP RFAN")
        if (self._radio.isFreon):
            self._frequency = self._radio.getSoftpotFreqs(0x00)[0]
        else:
            if (self._radio.bandsplit == 'T'):
                self._frequency = 869.8875
    def performTest(self):
        self._logger.info("Beginning reference oscillator test")
        self._radio.setPowerLevel(3)
        self._radio.send(b'\x00\x02\x10')
        self._radio.setTXFrequency(self._frequency)
        self._instrument.setRXFrequency(self._frequency * 1000000)
        self._radio.keyRadio()
        time.sleep(4)
        err = round(self._instrument.measureRFError(self._frequency * 1000000), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = "Measured Frequency Error at {}MHz: {}hz\n".format(self._frequency, err)
        self._logger.info(logLine)
        self.report = logLine
        self.report += '\n'
    def tearDown(self):
        pass
