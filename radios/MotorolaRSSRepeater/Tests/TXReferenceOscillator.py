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
        self.report += logLine
        self.report += '\n'
        self.testResult = err
        return err

    def isCompliant(self):
        if (self._tolerance * -1 < self.testResult < self._tolerance):
            return True
        return False

    def performAlignment(self):
        bmeas = self.performTest()
        self._logger.debug("Beginning alignment")
        bsp = self._radio.get('AL PEND RD', prependGet=False)
        self._logger.debug("Beginning softpot value: {}".format(bsp))
        self.report += 'Beginning softpot value: {}\n'.format(bsp)


        engine = AutoTuneEngine(self.performTest, self.setSoftpotCallback, bsp, bmeas, 0)
        engine.tune()
        #give it a moment to commit the softpot
        time.sleep(1)
        self._radio.send('AL PEND SAVE')
        time.sleep(1)

        esp = self._radio.get('AL PEND RD', prependGet=False)
        self._logger.debug("Ending softpot value: {}".format(esp))
        self.report += "Ending softpot value: {}\n".format(esp)

    def setSoftpotCallback(self, spval):
        self.report += 'Trying new softpot value {}\n'.format(spval)
        #quantar is relative, so we have to read the softpot, then adjust it so many steps
        csp = float(self._radio.get('AL PEND RD', prependGet=False))
        #print("Starting softpot {}".format(csp))
        delta = round(abs(csp - spval))
        dir = ""
        # the quantar number thing is reversed
        # during testing if i had a softpot at 90, then moved it down 5 steps, it would then be at 95
        if (spval < csp):
            dir = 'UP'
        else:
            dir = 'DN'

        #print("Moving pendulum {} {} steps".format(dir, delta))
        self._radio.send('AL PEND {} {}'.format(dir, delta))
        time.sleep(1)
        #print("New sp: {}".format(float(self._radio.get('AL PEND RD', prependGet=False))))

    def tearDown(self):
        pass
