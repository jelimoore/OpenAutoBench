import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
from openautobench.AutoTuneEngine import AutoTuneEngine
import time

class testTxReferenceOscillator_RSS(AutoTest):
    name = "Tx - Reference Oscillator"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequency = None
        self._logger = logging.getLogger(__name__)
        self.report = ''
        self._autotuner = None
        self._tolerance = 25

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument._sendCmd("DISP RFAN")
        self._radio.setCurrentShell('RSS')
        self._frequency = self._radio.getTXFrequency()
        self._radio.send('DEKEY')
        #self._radio.send('SET EEP TXDEV -1')
        
    def performTest(self):
        self._radio.keyRadio()
        self._instrument.setRXFrequency(self._frequency)
        #self._radio.setPowerLevel(3)
        #self._radio.updateSoftpotValue(0x00, self.new_softpot, self._softpotNumBytes)
        time.sleep(7)
        err = round(self._instrument.measureRFError(self._frequency), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = "Measured Frequency Error at {}MHz: {}hz".format(self._frequency/1000000, err)
        self._logger.info(logLine)
        self.report = logLine
        self.report += '\n\n'
        return err

    def performAlignment(self):
        pass

    def tearDown(self):
        pass
