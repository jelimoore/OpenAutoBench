import logging
from .. import interface
from builtins import NotImplementedError
from radios.MotorolaCommon.Tests.RXFrontEndGain import protoRxFrontEndGain
import time

class testRxFrontEndGain(protoRxFrontEndGain):
    def isRadioEligible(self):
        if (self._radio.bandsplit == "Q" or
            self._radio.bandsplit == "T" or
            self._radio.bandsplit == "R"):
            return True
        else:
            return False

    def setup(self):
        super().setup()
        if (self._radio.bandsplit == "Q" and self._radio.formFactor == 'M'):
            self._frequency = 436.65
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'H'):
            self._frequency = 486.525
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'M'):
            self._frequency = 487.275
        if (self._radio.bandsplit == "R" and self._radio.formFactor == 'H'):
            self._frequency = 465.050

        # per service manual, use -75dbm for 2.0/2.5 port, light port, SL ports
        if (self._radio.isGen2 and self._radio.formFactor == 'H'):
            self._outputLevel = -75
        else:
            self._outputLevel = -80
