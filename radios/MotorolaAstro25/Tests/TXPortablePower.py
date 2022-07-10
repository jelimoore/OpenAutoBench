import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxPortablePower(AutoTest):
    name = "Tx - High/Medium/Low Power Test (Portable)"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self._lpTestpoints = []
        self._hpTestpoints = []
        self.report = ''

    def isRadioEligible(self):
        if ('H18Q' in self._radio.modelNumber or 
            'H18K' in self._radio.modelNumber or
            'H18U' in self._radio.modelNumber or
            'M20K' in self._radio.modelNumber or
            'M21K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber or
            'M20U' in self._radio.modelNumber or
            'M21U' in self._radio.modelNumber or
            'L20U' in self._radio.modelNumber or):
            return True
        return False

    def setup(self):
        self._instrument.setDisplay("RFAN")
        if ('H18Q' in self._radio.modelNumber):
            self._frequencies = [
                380.025,
                390.025,
                400.025,
                411.025,
                424.925,
                425.025,
                435.025,
                445.025,
                457.025,
                469.925
            ]

        if ('H18K' in self._radio.modelNumber):
            self._frequencies = [
                136.075,
                142.075,
                154.275,
                160.175,
                168.125,
                173.925
            ]
        
        if ('L20K' in self._radio.modelNumber or
            'M20K' in self._radio.modelNumber or
            'M21K' in self._radio.modelNumber):
            self._frequencies = [
                136.0125,
                140.7625,
                145.5125,
                150.2625,
                154.9875,
                155.0125,
                159.7625,
                164.5125,
                169.2625
            ]
        
        if ('L20U' in self._radio.modelNumber or
            'M20U' in self._radio.modelNumber or
            'M21U' in self._radio.modelNumber):
            self._frequencies = [
                762.0125,
                769.0125,
                775.9875,
                794.0125,
                805.9875,
                806.0125,
                823.9875,
                851.0125,
                860.0125,
                869.8875
            ]
        
        #TODO: make this use the common softpot read function
        self._radio.setPowerLevel(0)
        softpotVals = (self._radio.send(b'\x00\x01\x03\x11'))
        # iterate over frequencies and create test points with the softpot value
        offset = 3
        for freq in self._frequencies:
            lowPoint = softpotVals[offset:offset+2]
            self._lpTestpoints.append({'freq': freq, 'softpot': lowPoint})
            offset += 2
            
            highPoint = softpotVals[offset:offset+2]
            self._hpTestpoints.append({'freq': freq, 'softpot': highPoint})
            offset += 2
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
