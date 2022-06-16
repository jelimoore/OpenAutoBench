import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxPortablePower(AutoTest):
    name = "Tx - High/Low Power Test (Portable)"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self._lpTestpoints = []
        self._hpTestpoints = []
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.isFreon and self._radio.formFactor == 'H' and 'H91' not in self._radio.modelNumber):
            return True
        return False

    def setup(self):
        self._instrument.setDisplay("RFAN")
        self._frequencies = self._radio.getSoftpotFreqs(0x01)
        self._radio.setPowerLevel(0)
        softpotVals = (self._radio.send(b'\x00\x01\x03\x11'))
        print(softpotVals)
        # iterate over frequencies and create test points with the softpot value
        offset = 3
        for freq in self._frequencies:
            lowPoint = softpotVals[offset:offset+2]
            self._lpTestpoints.append({'freq': freq, 'softpot': lowPoint})
            offset += 2
            
            highPoint = softpotVals[offset:offset+2]
            self._hpTestpoints.append({'freq': freq, 'softpot': highPoint})
            offset += 2
        print(self._hpTestpoints)
        print(self._lpTestpoints)
        # set mode analog
        self._radio.send(b'\x00\x02\x10')

    def performTest(self):
        self._logger.info("Testing low power")
        self._radio.setPowerLevel(3)
        self.report += 'Low Power:\n'
        for tp in self._lpTestpoints:
            freq = tp['freq']
            sp = tp['softpot']
            self._logger.info("Frequency {} - existing softpot {}".format(freq, int.from_bytes(sp, "big")))
            self._radio.setTXFrequency(freq)
            self._instrument.setRXFrequency(freq * 1000000)
            self._radio.keyRadio()
            self._radio.send(b'\x00\x01\x02\x01' + sp)
            time.sleep(4)
            pow = round(self._instrument.measureRFPower(), 2)
            self._logger.info("Power: {}w".format(pow))
            self.report += 'Measured power at {}MHz: {}w\n'.format(freq, pow)
            self._radio.unkeyRadio()
            time.sleep(1)

        self._logger.info("Testing high power")
        self._radio.setPowerLevel(0)
        self.report += 'High Power:\n'
        for tp in self._hpTestpoints:
            freq = tp['freq']
            sp = tp['softpot']
            self._logger.info("Frequency {} - existing softpot {}".format(freq, int.from_bytes(sp, "big")))
            self._radio.setTXFrequency(freq)
            self._instrument.setRXFrequency(freq * 1000000)
            self._radio.keyRadio()
            self._radio.send(b'\x00\x01\x02\x01' + sp)
            time.sleep(4)
            pow = round(self._instrument.measureRFPower(), 2)
            self._logger.info("Power: {}w".format(pow))
            self.report += 'Measured power at {}MHz: {}w\n'.format(freq, pow)
            self._radio.unkeyRadio()
            time.sleep(1)
        self.report += '\n'
            
    def performAlignment(self):
        raise NotImplementedError

    def tearDown(self):
        pass
