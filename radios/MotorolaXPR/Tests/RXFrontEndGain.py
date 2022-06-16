# Q: 403.15, 447.725
# T: 464.075

# gain and atten
# Q: 436.65
# T: 486.525
import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testRxFrontEndGain(AutoTest):
    name = "RX - Front End Gain"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequency = None
        self._outputLevel = None
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.bandsplit == "Q" or
            self._radio.bandsplit == "T"):
            return True
        else:
            return False

    def setup(self):
        self._instrument._sendCmd("DISP RFG")
        if (self._radio.bandsplit == "Q"):
            self._frequency = 436.65
        if (self._radio.bandsplit == "T"):
            self._frequency = 511.825
        if (self._radio.bandsplit == "R"):
            self._frequency = 477.425

        # per service manual, use -75dbm for 2.0/2.5 port, light port, SL ports
        if (self._radio.isGen2 and self._radio.formFactor == 'H'):
            self._outputLevel = -75
        else:
            self._outputLevel = -80

    def performTest(self):
        self._logger.info("Beginning Front End Gain Test")
        self._instrument.generateRFSignal(self._frequency * 1000000, self._outputLevel)
        self._radio.setRXFrequency(self._frequency)
        time.sleep(3)
        rssi = 0
        for i in range(0,3):
            thisRssi = self._radio.readRSSI()
            rssi += thisRssi
            self._logger.debug("RSSI reading #{}: {}".format(i, thisRssi))
            time.sleep(1)

        logLine = "Reported RSSI at {}: {}".format(self._frequency, rssi / 3)
        self._logger.info(logLine)
        self.report = logLine + '\n'
        # shut off freqgen
        self._instrument.generateRFSignal(self._frequency * 1000000, -137)
        

    def tearDown(self):
        pass
