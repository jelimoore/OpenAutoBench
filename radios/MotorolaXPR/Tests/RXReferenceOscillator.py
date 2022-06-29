import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
from openautobench.AutoTuneEngine import AutoTuneEngine
import time

class testRxReferenceOscillator(AutoTest):
    name = "Rx - Reference Oscillator"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequency = None
        self._logger = logging.getLogger(__name__)
        self._outputLevel = 0
        self.old_softpot = 0
        self.new_softpot = 0
        self._softpotNumBytes = 1   # default to 1 byte per softpot
        self.report = ''
        self._autotuner = None
        self._tolerance = 15

    def isRadioEligible(self):
        if (self._radio.isRepeater and 'M27' in self._radio.modelNumber and self._radio.bandsplit == 'T'):
            return True
        return False

    def setup(self):
        currentMode = self._radio.getStatus(0x0d)[2]
        if (currentMode == 0x01):
            raise Exception("Repeater is in digital mode. You must set it to an analog personality in CPS to perform testing.")
        if (self._radio.bandsplit == "T"):
            self._frequency = 526.925
            self._outputLevel = -80

        self.old_softpot = self._radio.getSoftpotValue(0x00, numBytes=self._softpotNumBytes)[0]
        self.new_softpot = self.old_softpot

    def performTest(self):
        self._logger.info("Beginning reference oscillator test")
        self._instrument.setRFOutputPort('DUPL')
        self._instrument.enableRFGenerator()
        self._instrument.generateRFSignal(self._frequency * 1000000, self._outputLevel)
        self._radio.send(b'\x00\x03\x10')
        self._radio.send(b'\x00\x1c\x02')
        self._radio.setRXFrequency(self._frequency)
        time.sleep(5)
        err = self._radio.send(b'\x00\x0e\x0c')[2:]
        
        err = int.from_bytes(err, "big")
        # two's complement
        if (err > 32767):
            err = ~err ^ 0xFFFF

        #print("Dekeying")
        self._radio.send(b'\x00\x1c\x01')
        self._instrument.disableRFGenerator()
        logLine = "Measured Frequency Error: {}hz".format(err)
        
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
