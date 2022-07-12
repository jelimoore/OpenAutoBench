import logging
from .. import interface
from builtins import NotImplementedError
from openautobench.AutoTuneEngine import AutoTuneEngine
import time
from radios.MotorolaRSSRepeater.Tests.TXReferenceOscillator import testTxReferenceOscillator_RSS

class testTxReferenceOscillator(testTxReferenceOscillator_RSS):
    def __init__(self, radio, instrument):
        super().__init__(radio, instrument)