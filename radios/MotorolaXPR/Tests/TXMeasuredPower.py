from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import logging
import time

class testTxMeasuredPower(AutoTest):
    name = "Tx - Measured Power (Mobile)"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self._testpoints = []
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.formFactor == 'M'):
            if (self._radio.bandsplit == "Q" and self._radio.powerLevel == "P"):
                return True
            else:
                return False
        else:
            return False

    def setup(self):
        self._instrument.setDisplay("RFAN")

        if (self._radio.bandsplit == "Q"):
            self._frequencies =[403.100,
                                414.250,
                                425.450,
                                436.600,
                                447.775,
                                458.950,
                                469.975]
        
        softpots = self._radio.send(b'\x00\x01\x03\x11')
        # iterate over frequencies and create test points with the softpot value
        offset = 3
        for freq in self._frequencies:
            sp = []
            for i in range(0,4):
                sp.append(softpots[offset:offset+2])
                offset += 2
            self._testpoints.append({'freq': freq, 'softpots': sp})

    def performTest(self):
        self._logger.info("Beginning Measured Power test")
        # set low power - 00 06 03
        self._radio.send(b'\x00\x06\x03')
        # set mode analog - 00 02 10
        self._radio.send(b'\x00\x02\x10')

        for tp in self._testpoints:
            freq = tp['freq']
            sps = tp['softpots']
            self._logger.info("Testing Frequency {}".format(freq))
            self._radio.setTXFrequency(freq)
            self._instrument.setRXFrequency(freq * 1000000)
            powerLine = "Measured Power at {}MHz:\t".format(freq)
            for sp in sps:
                self._logger.debug("Testing softpot value {}".format(sp))
                self._radio.keyRadio()
                self._radio.send(b'\x00\x01\x02\x01' + sp)
                time.sleep(4)
                power = round(self._instrument.measureRFPower(), 2)
                self._logger.debug("Measured power {}w".format(power))
                self._radio.unkeyRadio()
                powerLine += "{}w\t".format(power)
                time.sleep(1.5)
            
            self._logger.info(powerLine)
            self.report+=powerLine + '\n'

        

    def performAlignment(self):
        raise NotImplementedError

    def tearDown(self):
        pass
