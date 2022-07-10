import logging
from .. import interface
from builtins import NotImplementedError
from radios.MotorolaCommon.Tests.RXFrontEndFilter import protoRxFrontEndFilter
import time

class testRxFrontEndFilter(protoRxFrontEndFilter):
    def isRadioEligible(self):
        if ('M20K' in self._radio.modelNumber or
            'M21K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber or
            'M20U' in self._radio.modelNumber or
            'M21U' in self._radio.modelNumber or
            'L20U' in self._radio.modelNumber or):
            return True
        return False

    def setup(self):
        super().setup()
        if ('M20K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber):
            self._frequencies = [
                146.0625,
                140.8125,
                145.5625,
                150.3125,
                154.9375,
                155.0625,
                159.8125,
                164.5625,
                169.3125
            ]

        if ('M20K' in self._radio.modelNumber or
            'L20K' in self._radio.modelNumber):
            self._frequencies = [
                762.0625,
                769.0625,
                775.9375,
                851.0625,
                860.0625,
                869.9375
            ]

        self._outputLevel = -90
