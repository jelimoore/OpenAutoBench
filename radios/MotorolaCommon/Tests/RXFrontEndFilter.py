import logging
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class protoRxFrontEndFilter(AutoTest):
    name = "RX - Front End Filter"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequencies = []
        self._outputLevel = None
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        return False

    def setup(self):
        self._instrument._sendCmd("DISP RFG")

    def performTest(self):
        self._logger.info("Beginning Front End Gain Test")
        if (self._radio.isRepeater):
            self._instrument.setRFOutputPort('DUPL')
        else:
            self._instrument.setRFOutputPort('RF OUT')
        self._instrument.enableRFGenerator()
        for freq in self._frequencies:
            self._instrument.generateRFSignal(freq * 1000000, self._outputLevel)
            self._radio.setRXFrequency(freq)
            time.sleep(3)
            rssi = 0
            for i in range(0,3):
                thisRssi = self._radio.readRSSI()
                rssi += thisRssi
                self._logger.debug("RSSI reading #{}: {}".format(i, thisRssi))
                time.sleep(1)

            logLine = "Reported RSSI at {}:\t{}dbm".format(freq, round(rssi / 3, 2))
            self._logger.info(logLine)
            self.report += logLine + '\n'
        # shut off freqgen
        self._instrument.disableRFGenerator()

    def tearDown(self):
        pass
