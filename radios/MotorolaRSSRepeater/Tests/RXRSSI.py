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
        self._instrument.setRFOutputPort('DUPL')
        self._outputLevel = -90
        # dummy command? might not be needed?
        #print(self._radio.send('GET PA ON'))
        print(self._radio.send('SET FREQ TX 0'))
        self._frequency = self._radio.getRXFrequency()

    def performTest(self):
        self._instrument.enableRFGenerator()
        self._instrument.generateRFSignal(self._frequency, self._outputLevel)
        time.sleep(3)
        rssi = 0
        for i in range(0,3):
            thisRssi = self._radio.readRSSI()
            rssi += thisRssi
            self._logger.debug("RSSI reading #{}: {}".format(i, thisRssi))
            time.sleep(1)

        avgRssi = round(rssi / 3, 2)
        logLine = "Reported RSSI at {}MHz:\t{}dbm".format(self._frequency / 1000000, avgRssi)
        self._logger.info(logLine)
        self.report += logLine + '\n'
        # shut off freqgen
        self._instrument.disableRFGenerator()
        return avgRssi

    def isCompliant(self):
        return False

    def performAlignment(self):
        self._logger.debug("Beginning alignment")
        meas = self.performTest()
        self.report += 'Beginning RSSI: {}\n'.format(meas)
        self._instrument.enableRFGenerator()
        self._instrument.generateRFSignal(self._frequency, self._outputLevel)
        time.sleep(3)
        result = self._radio.send('AL RSSI {}'.format(abs(self._outputLevel)))
        #print(result)
        time.sleep(1)
        self._instrument.disableRFGenerator()
        meas = self.performTest()
        self.report += 'Ending RSSI: {}\n'.format(meas)

    def tearDown(self):
        pass
