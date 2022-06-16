class MotorolaIP():
    def __init__(self, ipAddress='0.0.0.0'):
        self.connected = False
        self._ipAddress = ipAddress
        self.modelNumber = ''
        self.serialNumber = ''
        self.codeplugVersion = ''
        self.firmwareVersion = ''
        self.tuningVersion = ''
        self.bootloaderVersion = ''
        self.bandsplit = ''
        self.formFactor = ''
        self.powerLevel = ''
        self._logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self._xnl.connect()
            self.modelNumber = self.send(b'\x00\x0e\x07')[2:].decode()
            self.serialNumber = self.send(b'\x00\x0e\x08')[2:].decode()
            self.firmwareVersion = self.send(b'\x00\x0f\x00')[2:].decode()
            self.codeplugVersion = self.send(b'\x00\x0f\x41')[1:].decode()
            self.tuningVersion = self.send(b'\x00\x0f\x50')[2:].decode()
            self.bootloaderVersion = self.send(b'\x00\x0f\x30')[2:].decode()

            self.bandsplit = self.modelNumber[3:4]
            self.powerLevel = self.modelNumber[4:5]
            self.formFactor = self.modelNumber[0:1]
            
            
            self._logger.debug("Model: {}".format(self.modelNumber))
            self._logger.debug("Serial: {}".format(self.serialNumber))
            self._logger.debug("Firmware: {}".format(self.firmwareVersion))
            self._logger.debug("Codeplug: {}".format(self.codeplugVersion))
            self._logger.debug("Tuning: {}".format(self.tuningVersion))
            self._logger.debug("Bootloader: {}".format(self.bootloaderVersion))
            self._logger.debug("Bandsplit: {}".format(self.bandsplit))
            self._logger.debug("Power Level: {}".format(self.powerLevel))
            self._logger.debug("Form Factor: {}".format(self.formFactor))

            connected = True
        except Exception as e:
            self._logger.debug(e)
            raise Exception("Failure connecting to radio")

    def disconnect(self):
        self._xnl.close()
    
    def send(self, toSend):
        return self.send(toSend)

    def setPowerLevel(self, index):
        self.send(b'\x00\x06' + index.to_bytes(1, "big"))

    def enterServiceMode(self):
        self.send(b'\x00\x0c')

    def resetRadio(self):
        self.send(b'\x00\x0d')

    def setTXFrequency(self, freq, lastByte=b'\x01'):
        xcmpFreq = int((freq * 1000000) / 5)
        self.send(b'\x00\x0b' + xcmpFreq.to_bytes(4, "big") + b'\x64' + lastByte)
    
    def setRXFrequency(self, freq, lastByte=b'\x00'):
        xcmpFreq = int((freq * 1000000) / 5)
        self.send(b'\x00\x0a' + xcmpFreq.to_bytes(4, "big") + b'\x32' + lastByte)

    def keyRadio(self):
        self.send(b'\x00\x04\x03')
    
    def unkeyRadio(self):
        self.send(b'\x00\x05\x11')
    
    def readRSSI(self):
        resp = self.send(b'\x00\x0e\x02')
        # parse incoming bytes to float
        return round(float("{}.{}".format(resp[2] * -1, resp[3])), 2)