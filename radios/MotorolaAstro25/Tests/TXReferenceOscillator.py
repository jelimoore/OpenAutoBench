import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
from openautobench.AutoTuneEngine import AutoTuneEngine
import time

class testTxReferenceOscillator(AutoTest):
    name = "Tx - Reference Oscillator"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequency = None
        self._logger = logging.getLogger(__name__)
        self.old_softpot = 0
        self.new_softpot = 0
        self._softpotNumBytes = 2   # default to 2 bytes per softpot
        self.report = ''
        self._autotuner = None
        self._tolerance = 25

    def isRadioEligible(self):
        if ('H18Q' in self._radio.modelNumber or 
            'H18K' in self._radio.modelNumber or
            'H18U' in self._radio.modelNumber or
            'M20K' in self._radio.modelNumber or
            'M21K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber or
            'M20U' in self._radio.modelNumber or
            'M21U' in self._radio.modelNumber or
            'L20U' in self._radio.modelNumber or):
            return True
        return False

    def setup(self):
        self._instrument._sendCmd("DISP RFAN")
        if ('H18Q' in self._radio.modelNumber):
            self._frequency = 469.975

        if ('H18K' in self._radio.modelNumber):
            self._frequency = 173.925

        if ('H18U' in self._radio.modelNumber):
            self._frequency = 869.8875
        
        if ('M20K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber or
            'M21K' in self._radio.modelNumber):
            self._frequency = 169.3125

        if ('M20U' in self._radio.modelNumber or
            'L20U' in self._radio.modelNumber or
            'M21U' in self._radio.modelNumber):
            self._frequency = 869.8875

        self._radio.send(b'\x00\x02\x10')
        self._radio.setTXFrequency(self._frequency)
        self._instrument.setRXFrequency(self._frequency * 1000000)
        self.old_softpot = self._radio.getSoftpotValue(0x00, self._softpotNumBytes)[0]
        self.new_softpot = self.old_softpot
    def performTest(self):
        self._radio.keyRadio()
        #self._radio.setPowerLevel(3)
        self._radio.updateSoftpotValue(0x00, self.new_softpot, self._softpotNumBytes)
        time.sleep(7)
        err = round(self._instrument.measureRFError(self._frequency * 1000000), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = "Measured Frequency Error at {}MHz: {}hz".format(self._frequency, err)
        self._logger.info(logLine)
        self.report = logLine
        self.report += '\n\n'

        return err

    def performAlignment(self):
        self._logger.info("Beginning softpot value: {}".format(self.old_softpot))
        initialAbs = self._frequency * 1000000 + self.performTest()
        self._autotuner = AutoTuneEngine(self.old_softpot, initialAbs, self._frequency * 1000000)
        self._logger.info("Performing alignment")

        while True:
            self.new_softpot = self._autotuner.currentSetting
            self._logger.info("Trying new softpot value {}".format(self.new_softpot))
            measAbs = self._frequency * 1000000 + self.performTest()
            self._autotuner.setCurrentMeasurement(measAbs)
            #print(measAbs)
            
            if (self._frequency * 1000000 - self._tolerance < measAbs and self._frequency * 1000000 + self._tolerance > measAbs):
                self._logger.info("Alignment complete. New softpot value: {}".format(self.new_softpot))
                self._radio.writeSoftpotValue(0x00, self.new_softpot, self._softpotNumBytes)
                break
        
        time.sleep(0.2)

    def tearDown(self):
        pass
