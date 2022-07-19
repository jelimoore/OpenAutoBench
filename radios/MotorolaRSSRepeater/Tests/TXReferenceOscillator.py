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
        self.testResult = None
        self._autotuner = None
        self._tolerance = 50
        self._curr_sp = 0

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
        time.sleep(7)
        err = round(self._instrument.measureRFError(self._frequency), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = "Measured Frequency Error at {}MHz: {}hz".format(self._frequency/1000000, err)
        self._logger.info(logLine)
        self.report = logLine
        self.report += '\n\n'
        self.testResult = err
        return err

    def isCompliant(self):
        if (self._tolerance * -1 < self.testResult < self._tolerance):
            return True
        return False

    def performAlignment(self):
        self._logger.debug("Beginning alignment")
        bsp = self._radio.get('AL PEND RD', prependGet=False)
        self._curr_sp = bsp
        self._logger.debug("Beginning softpot value: {}".format(bsp))

        #engine = AutoTuneEngine(self.performTest, self.setSoftpotCallback, bsp)
        #engine.tune()
        #self._radio.send('AL PEND SAVE')

        esp = self._radio.get('AL PEND RD', prependGet=False)
        self._logger.debug("Ending softpot value: {}".format(esp))

    def setSoftpotCallback(self, spval):
        dir = ""
        val = abs(spval - self._curr_sp)
        if (spval > self._curr_sp):
            dir = 'UP'
        else:
            dir = 'DOWN'

        self._radio.send('AL PEND {} {}'.format(dir, val))
        self._curr_sp = spval

    def tearDown(self):
        pass
