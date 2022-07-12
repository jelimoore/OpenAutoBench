import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.common import AutoTest
import time
from radios.MotorolaRSSRepeater.Tests.TXPower import testTxPower_RSS

class testTxPower(testTxPower_RSS):
    def __init__(self, radio, instrument):
        super().__init__(radio, instrument)