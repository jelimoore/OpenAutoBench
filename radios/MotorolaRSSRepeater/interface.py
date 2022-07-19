from builtins import ConnectionError
import warnings
import logging
import time
import serial

class MotorolaRSSRepeater():
    def __init__(self, serialPort, baud=9600):
        self.connected = False
        self._serialPort = serial.Serial(serialPort,
                                         baudrate=baud,
                                         timeout=1,
                                         xonxoff=0)
                                         #rtscts=0)
        self.stationName = ''
        self.serialNumber = ''
        self.codeplugVersion = ''
        self.hardware = ''
        self.rx1Band = ''
        self.rx2Band = ''
        self.txBand = ''
        self.txPower = ''
        self.hardwareVersion = ''
        self._currentShell = None
        self._logger = logging.getLogger(__name__)

    def connect(self):
        if (self._serialPort.is_open):
            #don't open an already open port
            pass
        else:
            self._serialPort.open()

        # send newline
        if (len(self.send('EXIT')) == 0):
            raise Exception("Got no response from the repeater.")
        #print(self.send('DORSS'))
        self.getCurrentShell()
        #print("Current shell: {}".format(self._currentShell))
        self.setCurrentShell('RSS')

    def disconnect(self):
        self.send('EXIT')
        self._serialPort.close()

    def send(self, commandIn):
        self._serialPort.reset_input_buffer()
        packet = commandIn.encode() + b'\r\n'
        #print("Sending {}".format(packet))
        self._serialPort.write(packet)

        # flush one line to clear the echoed line (what you send comes back)
        echoLine = self._serialPort.readline()
        #print("Read {}".format(echoLine))
        line = self._serialPort.readline()
        #print("Read {}".format(line))
        line = line.replace(b'\r', b'')
        line = line.replace(b'\n', b'')
        line = line.decode()
        if (line.startswith('?')):
            raise Exception("Repeater returned error: {}".format(line))
        return line

    def getCurrentShell(self):
        result = self.send('')
        if (']-O' in result):
            self._currentShell = 'MAIN'
        elif ('RSS' in result):
            self._currentShell = 'RSS'
        elif ('RAP' in result):
            self._currentShell = 'RAP'
        else:
            self._currentShell = None
            self._logger.warning("Got unknown shell prompt: {}".format(result))
    
    def setCurrentShell(self, shell):
        self.getCurrentShell()
        if (self._currentShell == shell):
            return
        else:
            self.send('EXIT')
            # if we are switching to main shell, don't enter a new shell, just exit
            if (shell != 'MAIN'):
                self.send('DO' + shell)


    def get(self, val, prependGet=True):
        command = ""
        if (prependGet):
            command = "GET " + val
        else:
            command = val
        result = self.send(command)
        result = result.split(' = ', 1)
        return result[1]

    def accessEnable(self):
        oldShell = self._currentShell
        self.setCurrentShell('RAP')
        self.send('FP ACC_DIS OFF')
        self.setCurrentShell(oldShell)
    
    def accessDisable(self):
        oldShell = self._currentShell
        self.setCurrentShell('RAP')
        self.send('FP ACC_DIS ON')
        self.setCurrentShell(oldShell)

    def reset(self):
        self.setCurrentShell('RSS')
        self.send('RESET')

    def keyRadio(self):
        self.send('KEYUP')

    def unkeyRadio(self):
        self.send('DEKEY')
    
    def getTXFrequency(self):
        return int(self.get('TX FREQ'))

    def getRXFrequency(self):
        return int(self.get('RX FREQ'))