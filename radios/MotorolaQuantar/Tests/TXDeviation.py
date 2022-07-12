import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxModBalance():
    name = "Tx - Modulation Balance"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self.report = ''

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument.setDisplay("AFAN")
        self._instrument._sendCmd("AFAN:FILT1 '<20Hz HPF'")
        self._instrument._sendCmd("AFAN:FILT2 '15kHz LPF'")

    def performTest(self):
        self._logger.info("Beginning Mod Balance test")

        for i in range(1,5):    # end is exclusive; we have 4 steps
            freq = self._radio.send('AL TXDEV GO F{}'.format(i))    # this returns the frequency, sets it, and keys
            freq = freq.split(' = ')[1]
            self._logger.info("Testing Frequency {}".format(freq))
            self._instrument.setRXFrequency(freq)
            self._radio.keyRadio()
            time.sleep(5)
            dev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("Deviation: {}hz".format(dev))
            self._radio.unkeyRadio()
            self.report += 'Deviation at {}MHz: {}hz\n'.format(freq, dev)
            time.sleep(2)            

        self.report += '\n'
    def tearDown(self):
        pass
