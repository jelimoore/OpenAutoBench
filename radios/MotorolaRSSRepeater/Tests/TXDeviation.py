import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time

class testTxModBalance_RSS():
    name = "Tx - Modulation Balance"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._logger = logging.getLogger(__name__)
        self._frequencies = []
        self.report = ''
        self._useGet = False
        self._range = 0
        self.testResult = None

    def isRadioEligible(self):
        return True

    def setup(self):
        self._instrument.setDisplay("AFAN")
        self._instrument._sendCmd("AFAN:FILT1 '<20Hz HPF'")
        self._instrument._sendCmd("AFAN:FILT2 '15kHz LPF'")

    def performTest(self):
        self._logger.info("Beginning Mod Balance test")
        returnArr = []

        for i in range(1,self._range + 1):    # end is exclusive; we have 4 steps
            if (self._useGet):
                freq = self._radio.send('AL TXDEV GET F{}'.format(i))    # this returns the frequency
                self._radio.send('AL TXDEV GO F{}'.format(i))   # sets it, and keys
            else:
                freq = self._radio.send('AL TXDEV GO F{}'.format(i))    # returns the frequency, sets it, and keys
            freq = int(freq.split(' = ')[1])
            if (freq == 0):
                continue
            self._logger.info("Testing Frequency {}".format(freq / 1000000))
            self._instrument.setRXFrequency(freq)
            self._radio.keyRadio()
            time.sleep(5)
            dev = round(self._instrument.measureFMDeviation(), 2)
            self._logger.info("Deviation: {}hz".format(dev))
            self._radio.unkeyRadio()
            self.report += 'Deviation at {}MHz: {}hz\n'.format(freq, dev)
            returnArr.append(dev)
            time.sleep(2)            

        self.report += '\n'
        self.testResult = returnArr
        return returnArr

    def isCompliant(self):
        return False

    def performAlignment(self):
        self._logger.debug("Beginning alignment")
        bsp = self._radio.get('AL TXDEV RD', prependGet=False)
        self._logger.debug("Beginning softpot value: {}".format(bsp))

        txDevStr = ""
        for dev in self.testResult:
            txDevStr += "{} ".format(round(dev))
        
        self._radio.send('AL TXDEV WR {}'.format(txDevStr))
        time.sleep(1)

        esp = self._radio.get('AL TXDEV RD', prependGet=False)
        self._logger.debug("Ending softpot value: {}".format(esp))

    def tearDown(self):
        pass
