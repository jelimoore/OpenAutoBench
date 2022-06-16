import time

from instruments.instrumentbase import InstrumentBase

import serial


class HPIBInterface(InstrumentBase):
    def __init__(self, port, hpibAddress):
        super()
        self._serialPort = serial.Serial(port, 
                                         baudrate=115200,
                                         timeout=2,
                                         xonxoff=0,
                                         rtscts=0,
                                         dsrdtr=True
                                         )
        self.hpibAddress = hpibAddress
        self.connected = False
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        if (self._serialPort.is_open):
            #don't open an already open port
            pass
        else:
            self._serialPort.open()

        # set up the HPIB adapter
        self._serialPort.write(b'++mode 1\r\n')
        adrString = b'++addr ' + str(self.hpibAddress).encode() + b'\r\n'
        self._serialPort.write(adrString)
        self._serialPort.write(b'++llo\r\n')
        self._serialPort.write(b'++auto 2\r\n')

        self._serialPort.reset_input_buffer()
        connected = True
        

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        self._serialPort.write(b'++loc\r\n')
        self._serialPort.write(b'++loc\r\n')
        self._serialPort.write(b'++loc\r\n')
        if (self._serialPort.is_open):
            self._serialPort.close()
        else:
            #don't close an already closed port
            pass

    def _sendCmd(self, cmd):
        self._serialPort.reset_input_buffer()
        if (self._serialPort.is_open):
            self._serialPort.write(cmd.encode())
            self._serialPort.write(b'\r\n')
        else:
            raise Exception("Serial port must be opened before attempting to send commands")

    def _readResponse(self):
        #set a timeout so we don't loop forever, 2 sec is probably fine
        line = self._serialPort.readline()
        # strip the newline
        line.replace(b'\n', b'')
        return line.decode()

    def _readMeasurement(self):
        resp = self._readResponse()
        try:
            val = float(resp)
            return val
        except:
            raise Exception("Tried to read a measurement value as a number, but couldn't. Received {}".format(resp))

    def getInfo(self):
        '''Method for retrieving info about the test set'''
        self._sendCmd('*IDN?')
        return self._readResponse()

    def setDisplay(self, screenName):
        self._sendCmd("DISP {}".format(screenName))

    def generateRFSignal(self, frequency, amplitude):
        '''Method for generating an RF signal at the specified frequency and amplitude'''
        self._sendCmd("RFG:FREQ " + str(frequency))
        self._sendCmd("RFG:AMPL " + str(amplitude) +" dBm")

    def measureFMDeviation(self):
        '''Method for measuring broadband power at the specified frequency'''
        self._sendCmd('MEAS:AFR:FM?')
        return float(self._readMeasurement())

    def measureRFPower(self):
        '''Method for measuring broadband power at the specified frequency'''
        self._sendCmd('MEAS:RFR:POW?')
        return float(self._readMeasurement())

    def setRXFrequency(self, frequency):
        '''Method for measuring RF frequency error at the specified frequency'''
        self._sendCmd('RFAN:FREQ ' + str(frequency))

    def measureRFError(self, frequency):
        '''Method for measuring RF frequency error at the specified frequency'''
        self._sendCmd('RFAN:FREQ?')
        currentFrequency = self._readMeasurement()

        if (currentFrequency != frequency):
            self._sendCmd('RFAN:FREQ ' + str(frequency))
            time.sleep(3)

        self._sendCmd('MEAS:RFR:FREQ:ERR?')
        return self._readMeasurement()
        
