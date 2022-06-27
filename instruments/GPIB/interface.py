import time
from instruments.SCPI.interface import SCPISerialInterface, SCPITCPInterface
import serial


class GPIBSerialInterface(SCPISerialInterface):
    def __init__(self, port, gpibAddress, baud=115200):
        super().__init__(port, baud)
        self.gpibAddress = gpibAddress
        self.connected = False
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        super().connect()

        # set up the HPIB adapter
        self._serialPort.write(b'++mode 1\r\n')
        adrString = b'++addr ' + str(self.gpibAddress).encode() + b'\r\n'
        self._serialPort.write(adrString)
        self._serialPort.write(b'++llo\r\n')
        self._serialPort.write(b'++auto 2\r\n')

        self._serialPort.reset_input_buffer()
        

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        self._serialPort.write(b'++loc\r\n')
        self._serialPort.write(b'++loc\r\n')
        self._serialPort.write(b'++loc\r\n')
        
        super().disconnect()

class GPIBTCPInterface(SCPITCPInterface):
    def __init__(self, ip, port, gpibAddress):
        super(ip, port)
        self.gpibAddress = gpibAddress
        self.connected = False
        
    def connect(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        super.connect()

        # set up the HPIB adapter
        self._socket.send(b'++mode 1\r\n')
        adrString = b'++addr ' + str(self.gpibAddress).encode() + b'\r\n'
        self._socket.send(adrString)
        self._socket.send(b'++llo\r\n')
        self._socket.send(b'++auto 2\r\n')

        self._serialPort.reset_input_buffer()
        

    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        self._socket.send(b'++loc\r\n')
        self._socket.send(b'++loc\r\n')
        self._socket.send(b'++loc\r\n')
        
        super.disconnect()
