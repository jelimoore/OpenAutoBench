import time
from instruments.instrumentbase import InstrumentBase
import socket
import serial


class SCPIBaseInterface(InstrumentBase):
    def __init__(self):
        super()
        self.connected = False
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        raise NotImplementedError("Method must be implemented in child class.")
        
    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        raise NotImplementedError("Method must be implemented in child class.")

    def _sendCmd(self, cmd):
        raise NotImplementedError("Method must be implemented in child class.")

    def _readResponse(self):
        raise NotImplementedError("Method must be implemented in child class.")

    def _readMeasurement(self):
        resp = self._readResponse()
        if (resp is None or resp == ""):
            return None
        try:
            val = float(resp)
            return val
        except:
            raise Exception("Tried to read a measurement value as a number, but couldn't. Received {}".format(resp))

    def getInfo(self):
        '''Method for retrieving info about the test set'''
        self._sendCmd('*IDN?')
        return self._readResponse()
    
    def reset(self):
        '''Method for resetting test set'''
        self._sendCmd('*RST')

    def setDisplay(self, screenName):
        self._sendCmd("DISP {}".format(screenName))

    def generateRFSignal(self, frequency, amplitude):
        '''Method for generating an RF signal at the specified frequency and amplitude'''
        self._sendCmd("RFG:FREQ " + str(frequency))
        self._sendCmd("RFG:AMPL " + str(amplitude) +" dBm")

    def enableRFGenerator(self):
        self._sendCmd('RFG:AMPL:STAT ON')

    def disableRFGenerator(self):
        self._sendCmd('RFG:AMPL:STAT OFF')

    def setRFOutputPort(self, port):
        # add quotes to terminate the string
        port = '"' + port + '"'
        self._sendCmd("RFG:OUTP " + str(port))

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
        


class SCPISerialInterface(SCPIBaseInterface):
    def __init__(self, port, baud):
        super()
        self._serialPort = serial.Serial(port, 
                                         baudrate=baud,
                                         timeout=2,
                                         xonxoff=0,
                                         rtscts=0,
                                         dsrdtr=True
                                         )
        self.connected = False
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        if (self._serialPort.is_open):
            #don't open an already open port
            pass
        else:
            self._serialPort.open()

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
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

class SCPITCPInterface(SCPIBaseInterface):
    def __init__(self, ip, port):
        super()
        self.connected = False
        self._ipAddress = ip
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        self._socket.connect((self._ipAddress, self._port))

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        self._socket.close()

    def _sendCmd(self, cmd):
        self._socket.send(cmd.encode())
        self._socket.send(b'\r\n')

    def _readResponse(self):
        #set a timeout so we don't loop forever, 2 sec is probably fine
        line = self._socket.recv(1024)
        # strip the newline
        line.replace(b'\n', b'')
        return line.decode()

import os
 
class SCPIUSBInterface(SCPIBaseInterface):
    """Simple implementation of a USBTMC device driver, in the style of visa.h"""
 
    def __init__(self, device):
        self.device = device
        self.FILE = os.open(device, os.O_RDWR)
 
    def __init__(self, port):
        super()
        self.connected = False
        self._port = None
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        self._port = os.open(device, os.O_RDWR)

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        pass

    def _sendCmd(self, cmd):
        os.write(self.FILE, cmd.encode())
        self._socket.send(b'\r\n')

    def _readResponse(self):
        return os.read(self.FILE, 1024)
        # strip the newline
        line.replace(b'\n', b'')
        return line.decode()