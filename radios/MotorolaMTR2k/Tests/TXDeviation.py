import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time
from radios.MotorolaRSSRepeater.Tests.TXDeviation import testTxModBalance_RSS

class testTxModBalance(testTxModBalance_RSS):
    def __init__(self, radio, instrument):
        super().__init__(radio, instrument)
    
    def setup(self):
        super().setup()
        self._useGet = True
        self._range = 8