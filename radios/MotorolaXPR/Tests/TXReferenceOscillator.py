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
        self._softpotNumBytes = 1   # default to 1 byte per softpot
        self.report = ''
        self._autotuner = None
        self._tolerance = 15

    def isRadioEligible(self):
        if (self._radio.bandsplit == "Q" or
            self._radio.bandsplit == "T" or
            self._radio.bandsplit == 'R'):
            return True
        else:
            return False

    def setup(self):
        currentMode = self._radio.getStatus(0x0d)[2]
        if (currentMode == 0x01):
            raise Exception("Repeater is in digital mode. You must set it to an analog personality in CPS to perform testing.")
        self._instrument._sendCmd("DISP RFAN")
        if (self._radio.bandsplit == "Q"):
            self._frequency = 469.975
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'H'):
            self._frequency = 511.825
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'M'):
            self._frequency = 527.0
        if (self._radio.bandsplit == "R" and self._radio.formFactor == 'H'):
            self._frequency = 477.425

        self.old_softpot = self._radio.getSoftpotValue(0x00, numBytes=self._softpotNumBytes)[0]
        self.new_softpot = self.old_softpot

    def performTest(self):
        self._logger.info("Beginning reference oscillator test")
        self._radio.setPowerLevel(3)
        self._radio.send(b'\x00\x02\x10')
        # set frequency 00 0b 05 9a 3f f8 64 01
        self._radio.setTXFrequency(self._frequency)
        self._instrument.setRXFrequency(self._frequency * 1000000)
        self._radio.keyRadio()
        self._radio.updateSoftpotValue(0x00, self.new_softpot, numBytes=self._softpotNumBytes)
        # sleep for a bit longer to let the radio warm up
        time.sleep(7)
        err = round(self._instrument.measureRFError(self._frequency * 1000000), 2)
        #print("Dekeying")
        self._radio.unkeyRadio()
        logLine = ''
        if (self._radio.isGen2):
            absFreq = float((self._frequency * 1000000) - err)
            logLine += "Absolute frequency: {}hz\n".format(absFreq)
            
        logLine += "Measured Frequency Error: {}hz".format(err)
        
        self._logger.info(logLine)
        self.report = logLine + '\n'
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
                self._radio.writeSoftpotValue(0x00, self.new_softpot, numBytes=self._softpotNumBytes)
                break
        
        time.sleep(0.2)

    def tearDown(self):
        pass
