import logging
from .. import interface
from builtins import NotImplementedError
from radios.MotorolaCommon.Tests.RXFrontEndGain import protoRxFrontEndGain
import time

class testRxFrontEndGain(protoRxFrontEndGain):
    def isRadioEligible(self):
        if (self._radio.isFreon):
            return True
        return False

    def setup(self):
        super().setup()
        #all APX radios use -75dbm output level
        self._outputLevel = -75
        self._frequencies = self._radio.getSoftpotFreqs(0x20)
        print(self._frequencies)
