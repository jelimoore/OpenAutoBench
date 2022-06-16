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
        if (self._radio.formFactor == 'H'):
            if (self._radio.bandsplit == "T" and self._radio.powerLevel == "D"):
                return True
            else:
                return False
        else:
            return False

    def setup(self):
        self._instrument.setDisplay("RFAN")

        if (self._radio.bandsplit == "T"):
            self._frequencies =[450.175,
                                464.175,
                                475.175,
                                486.625,
                                496.775,
                                504.775,
                                511.825]
        
        if (self._radio.bandsplit == "R"):
            self._frequencies =[403.025,
                                415.425,
                                427.825,
                                440.225,
                                452.625,
                                465.025,
                                477.425,
                                489.825,
                                502.225,
                                514.625,
                                526.975]

        self._radio.setPowerLevel(0)
        softpot_high = (self._radio.send(b'\x00\x01\x03\x01'))
        # iterate over frequencies and create test points with the softpot value
        offset = 3
        for freq in self._frequencies:
            softpotPoint = softpot_high[offset:offset+2]
            self._hpTestpoints.append({'freq': freq, 'softpot': softpotPoint})
            offset += 2
        print(self._hpTestpoints)

        # repeat for low power
        self._radio.setPowerLevel(3)
        softpot_low = (self._radio.send(b'\x00\x01\x03\x01'))
        # iterate over frequencies and create test points with the softpot value
        offset = 3
        for freq in self._frequencies:
            softpotPoint = softpot_low[offset:offset+2]
            self._lpTestpoints.append({'freq': freq, 'softpot': softpotPoint})
            offset += 2
        print(self._hpTestpoints)

        # set mode analog
        self._radio.send(b'\x00\x02\x10')

    def performTest(self):
        self._logger.info("Testing low power")
        self._radio.setPowerLevel(3)
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
            self._radio.unkeyRadio()
            time.sleep(1)

        self._logger.info("Testing high power")
        self._radio.setPowerLevel(0)
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
            self._radio.unkeyRadio()
            time.sleep(1)
            

    def performAlignment(self):
        raise NotImplementedError

    def tearDown(self):
        pass
