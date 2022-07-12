from builtins import ConnectionError
import warnings
import logging
import time
import serial

class MotorolaQuantar():
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
        self.firmwareVersions = {}
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
        if (len(self.send('')) == 0):
            raise Exception("Got no response from the Quantar. ")
        #print(self.send('DORSS'))
        self.getCurrentShell()
        #print("Current shell: {}".format(self._currentShell))
        self.setCurrentShell('RSS')
        
        #flush the port by sending a couple version requests
        #for i in range(0,2):
        #    print(self.getVersion())
        try:
            self.getVersion()
            self.stationName = self.get('STN NAME')
            self.serialNumber = self.get('STN SN')
            self.codeplugVersion = self.get('CP VER')
            self.rx1Band = self.get('RX FREQ_BAND')
            self.rx2Band = self.get('RX2 FREQ_BAND')
            self.txBand = self.get('TX FREQ_BAND')
            self.hardwareVersion = self.get('HW_VER')
            self.getHardware()

            self._logger.debug("Station Name: {}".format(self.stationName))
            self._logger.debug("Serial: {}".format(self.serialNumber))
            self._logger.debug("Firmware: {}".format(self.firmwareVersions))
            self._logger.debug("Codeplug: {}".format(self.codeplugVersion))
            self._logger.debug("Hardware: {}".format(self.hardware))
            self._logger.debug("RX Band: {}".format(self.rx1Band))
            self._logger.debug("RX 2 Band: {}".format(self.rx2Band))
            self._logger.debug("TX Band: {}".format(self.txBand))
            self._logger.debug("Hardware Version: {}".format(self.hardwareVersion))

            connected = True
        except Exception as e:
            self._logger.debug(e)
            raise Exception("Failure connecting to radio")

    def disconnect(self):
        self.send('EXIT')
        self._serialPort.close()

    def send(self, commandIn):
        self._serialPort.reset_input_buffer()
        packet = commandIn.encode() + b'\n'
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
            raise Exception("Quantar returned error: {}".format(line))
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


    def get(self, val):
        result = self.send("GET " + val)
        result = result.split(' = ', 1)
        return result[1]

    def getVersion(self):
        self.firmwareVersions['Control'] = self.get('FW_VER SC')
        self.firmwareVersions['Exciter'] = self.get('FW_VER EX')
        self.firmwareVersions['Wireline'] = self.get('FW_VER WL')
        self.firmwareVersions['Boot1'] = self.get('FW_VER BOOT.O')
        self.firmwareVersions['Boot2'] = self.get('FW_VER BOOT2.O')

    def getHardware(self):
        self.hardware += 'RX: {}, '.format(self.get('RX TYPE'))
        self.hardware += 'PA: {}, '.format(self.get('PA TYPE'))
        self.txPower = self.get('PA ORD_PWR')
        self.hardware += 'PA Power: {}, '.format(self.txPower)
        self.hardware += 'TX: {}, '.format(self.get('TX COMPA'))
        self.hardware += 'Wireline: {}, '.format(self.get('WL PORT_STAT'))
        self.hardware += 'Power: {}, '.format(self.get('PS RATED_PWR'))
        self.hardware += 'Battery: {} '.format(self.get('PS BATT_TYPE'))

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