import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time
import statistics

class testRxRSSIPlot(AutoTest):
    name = "Rx - RSSI Plot"
    def __init__(self, radio, instrument, uplink=None, downlink=None):
        self._radio = radio
        self._instrument = instrument
        self._testPoints = []
        if (uplink is not None):
            self._testPoints = [uplink]
        else:
            self._testPoints = [450]
        self._logger = logging.getLogger(__name__)
        self.report = ''
        self._rssiFile = ''
        self.dbStart = -130
        self.dbEnd = -30
        self.step = 1

    def isRadioEligible(self):
        if (self._radio.isHotspot):
            return False
        else:
            return True

    def setup(self):
        self._instrument._sendCmd("DISP RFG")
        self._radio.setMode(interface.STATE_RSSI_CAL)

    def performTest(self):
        for freq in self._testPoints:
            for db in range(self.dbStart, self.dbEnd, self.step):
                self._instrument.generateRFSignal(freq * 1000000, db)
                time.sleep(2)
                min, max, ave = self._radio.readRSSI()
                logLine = "Measured ADC value at {}dbm: {}".format(db, ave)
                self._rssiFile += '{}\t\t{}\n'.format(ave, db)
                self._logger.info(logLine)
            time.sleep(1)
        self.report += 'RSSI Map File:\n'
        self.report += self._rssiFile

    def tearDown(self):
        self._radio.setMode(interface.STATE_IDLE)
