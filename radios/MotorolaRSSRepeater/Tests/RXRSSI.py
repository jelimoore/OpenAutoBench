import logging
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testRxRSSI_RSS(AutoTest):
    name = "RX - RSSI"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequencies = []
        self._outputLevel = None
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument._sendCmd("DISP RFG")
        self._outputLevel = -90
        self._frequency = self._radio.getRXFrequency()

    def performTest(self):
        self._instrument.setRFOutputPort('DUPL')
        self._instrument.enableRFGenerator()
        self._instrument.generateRFSignal(self._frequency, self._outputLevel)
        time.sleep(3)
        rssi = 0
        for i in range(0,3):
            thisRssi = self._radio.readRSSI()
            rssi += thisRssi
            self._logger.debug("RSSI reading #{}: {}".format(i, thisRssi))
            time.sleep(1)

        logLine = "Reported RSSI at {}:\t{}dbm".format(self._frequency, round(rssi / 3, 2))
        self._logger.info(logLine)
        self.report += logLine + '\n'
        # shut off freqgen
        self._instrument.disableRFGenerator()

    def tearDown(self):
        pass
