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
        if ('H18Q' in self._radio.modelNumber or 'H18K' in self._radio.modelNumber):
            return True
        return False

    def setup(self):
        self._instrument.setDisplay("AFAN")
        self._instrument._sendCmd("AFAN:FILT1 '<20Hz HPF'")
        self._instrument._sendCmd("AFAN:FILT2 '15kHz LPF'")
        
        if ('H18Q' in self._radio.modelNumber):
            self._frequencies = [
                380.075,
                390.075,
                400.075,
                411.075,
                424.975,
                425.075,
                435.075,
                445.075,
                457.075,
                469.975
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
            'M20K' in self._radio.modelNumber):
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

    def performTest(self):
        self._logger.info("Beginning Mod Balance test")
        self._radio.setPowerLevel(3)

        for freq in self._frequencies:
            self._logger.info("Testing Frequency {}".format(freq))
            self._radio.setTXFrequency(freq, lastByte=b'\x00')
            self._instrument.setRXFrequency(freq * 1000000)
            # low tone
            self._radio.send(b'\x00\x02\x11')
            self._radio.keyRadio()
            time.sleep(5)
            lowdev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("Low tone: {}hz".format(lowdev))
            self._radio.unkeyRadio()
            time.sleep(1)

            # high tone
            self._radio.send(b'\x00\x02\x12')
            self._radio.keyRadio()
            time.sleep(5)
            highdev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("High Tone: {}hz".format(highdev))
            self._radio.unkeyRadio()
            time.sleep(1)

            self.report += 'Deviation at {}MHz: {}hz low tone, {}hz high tone\n'.format(freq, lowdev, highdev)

        self.report += '\n'
    def tearDown(self):
        pass
