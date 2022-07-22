import logging
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time
from radios.MotorolaRSSRepeater.Tests.RXRSSI import testRxRSSI_RSS

class testRxRSSI(testRxRSSI_RSS):
    def __init__(self, radio, instrument):
        super().__init__(radio, instrument)
