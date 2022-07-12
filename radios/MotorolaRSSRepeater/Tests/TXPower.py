import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxPower_RSS(AutoTest):
    name = "Tx - Power"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequency = None
        self.report = ''

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument.setDisplay("RFAN")
        self._frequency = self._radio.getTXFrequency()

    def performTest(self):
        self._logger.info("Testing power output")
        self._radio.send('AL STNPWR RESET')
        self._radio.send('SET TX PWR 100')
        self._instrument.setRXFrequency(self._frequency)
        self._radio.keyRadio()
        time.sleep(5)
        pow = round(self._instrument.measureRFPower(), 2)
        self._logger.info("Power: {}w".format(pow))
        self.report += 'Measured power at {}MHz: {}w\n'.format(self._frequency, pow)
        self._radio.unkeyRadio()
        self.report += '\n'
            
    def performAlignment(self):
        raise NotImplementedError

    def tearDown(self):
        pass
