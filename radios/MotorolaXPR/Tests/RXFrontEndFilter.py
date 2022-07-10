# Q: 403.15, 447.725
# T: 464.075

# gain and atten
# Q: 436.65
# T: 486.525
import logging
from .. import interface
from builtins import NotImplementedError
from radios.MotorolaCommon.Tests.RXFrontEndFilter import protoRxFrontEndFilter
import time

class testRxFrontEndFilter(protoRXFrontEndFilter):
    name = "RX - Front End Filter"
    def __init__(self, radio, instrument):
        self._radio = radio
        self._instrument = instrument
        self._frequencies = []
        self._outputLevel = None
        self._logger = logging.getLogger(__name__)
        self.report = ''

    def isRadioEligible(self):
        if (self._radio.formFactor == 'M' and self._radio.isGen2):
            return False
        if (self._radio.bandsplit == "Q" or
            self._radio.bandsplit == "T"):
            return True
        else:
            return False

    def setup(self):
        self._instrument._sendCmd("DISP RFG")
        if (self._radio.bandsplit == "Q" and self._radio.formFactor == 'M'):
            self._frequencies = [
                403.150,
                414.325,
                425.500,
                436.650,
                447.725,
                458.900,
                469.925
            ]
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'H'):
            self._frequencies = [
                450.075,
                464.075,
                475.075,
                486.525,
                496.875,
                504.875,
                511.875
            ]
        if (self._radio.bandsplit == "T" and self._radio.formFactor == 'M'):
            self._frequencies = [
                450.075,
                462.475,
                474.875,
                487.275,
                499.675,
                512.075,
                512.075050,
                519.575,
                526.925
            ]

        # per service manual, use -75dbm for 2.0/2.5 port, light port, SL ports
        if (self._radio.isGen2 and self._radio.formFactor == 'H'):
            self._outputLevel = -75
        else:
            self._outputLevel = -80

    def tearDown(self):
        pass
