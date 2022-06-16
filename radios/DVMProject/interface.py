import serial
import time
import logging

DVM_FRAME_START = b'\xFE'

CMD_GET_VERSION = b'\x00'
CMD_GET_STATUS  = b'\x01'
CMD_SET_CONFIG  = b'\x02'
CMD_SET_MODE    = b'\x03'
CMD_SET_SYMLVL  = b'\x04'
CMD_SET_RXLEVEL = b'\x05'
CMD_SET_RFPARAM = b'\x06'
CMD_CAL_DATA    = b'\x08'

STATE_IDLE      = b'\x00'
STATE_DMR       = b'\x01'
STATE_P25       = b'\x02'
STATE_P25_CAL   = b'\x61'
STATE_DMR_CAL   = b'\x62'

class DVMProjectInterface():
    def __init__(self, port):
        self._serialPort = serial.Serial(port,
                                         baudrate=115200,
                                         timeout=2,
                                         xonxoff=0)
                                         #rtscts=0)
        self.connected = False
        self.uid = ''
        self.versionString = ''
        self.cpu_type = ''
        self.isHotspot = False
        # RF params
        self._rxFrequency = 455000000
        self._txFrequency = 450000000
        self._rfPower = 100
        self._dmrDiscBWAdj = 0
        self._p25DiscBWAdj = 0
        self._dmrPostBWAdj = 0
        self._p25PostBWAdj = 0
        self._adfGainMode = 0
        self._dmrSym1Adj = 0
        self._dmrSym3Adj = 0
        self._p25Sym1Adj = 0
        self._p25Sym3Adj = 0

        # config params
        self.rxInvert = False
        self.txInvert = False
        self.pttInvert = False
        self.debug = False
        self.duplex = True
        self.dcBlock = True
        self.cosLockout = False
        self.dmrEnabled = False
        self.p25Enabled = True
        self.fdmaPreamble = 80
        self.current_state = STATE_IDLE
        self.rxLevel = 0
        self.cwidLevel = 0
        self.dmrColorCode = 1
        self.dmrRxDelay = 7
        self.p25Nac = 0x293
        self.dmrTxLevel = 50
        self.p25TxLevel = 50
        self.txDCOffset = 0
        self.rxDCOffset = 0
        self.p25CorrCount = 8

        self._logger = logging.getLogger(__name__)

    def connect(self):
        if (self._serialPort.is_open):
            #don't open an already open port
            pass
        else:
            self._serialPort.open()
        
        #flush the port by sending a couple version requests
        #for i in range(0,2):
        #    print(self.getVersion())
        self._versionString = self.getVersion()
        self.getStatus()
        connected = True

    def disconnect(self):
        self._serialPort.close()

    def getVersion(self):
        self._send(b'\x00')
        resp = self._receive()
        
        if (resp[2] != 0x02):
            raise Exception("Unsupported protocol version {}".format(resp[2]))

        for i in range(4,21):
            self.uid += str(hex(resp[i])[2:])

        self.versionString = resp[20:].decode()
        #print(self.versionString)
        #print(self.uid)
        return self.versionString

    def getStatus(self):
        self._send(CMD_GET_STATUS)
        resp = self._receive()
        self.isHotspot = (resp[2] & 0x01) == 0x01
        # rest of the command is not implemented

    def setRXFrequency(self, freq):
        self._rxFrequency = int(freq * 1000000)
        self.sendRFConfig()
    
    def setTXFrequency(self, freq):
        self._txFrequency = int(freq * 1000000)
        self.sendRFConfig()

    def setMode(self, mode):
        self.current_state = mode
        self.sendConfig()

    def sendRFConfig(self):
        command = CMD_SET_RFPARAM
        command += b'\x00'
        command += int((self._rxFrequency >> 0) & 0xFF).to_bytes(1, "big")
        command += int((self._rxFrequency >> 8) & 0xFF).to_bytes(1, "big")
        command += int((self._rxFrequency >> 16) & 0xFF).to_bytes(1, "big")
        command += int((self._rxFrequency >> 24) & 0xFF).to_bytes(1, "big")

        command += int((self._txFrequency >> 0) & 0xFF).to_bytes(1, "big")
        command += int((self._txFrequency >> 8) & 0xFF).to_bytes(1, "big")
        command += int((self._txFrequency >> 16) & 0xFF).to_bytes(1, "big")
        command += int((self._txFrequency >> 24) & 0xFF).to_bytes(1, "big")

        command += int(self._rfPower * 2.55 + 0.5).to_bytes(1, 'big')

        command += int(self._dmrDiscBWAdj + 128).to_bytes(1, "big")
        command += int(self._p25DiscBWAdj + 128).to_bytes(1, "big")
        command += int(self._dmrPostBWAdj + 128).to_bytes(1, "big")
        command += int(self._p25PostBWAdj + 128).to_bytes(1, "big")

        command += b'\x00'  # adf gain

        self._send(command)

    def sendConfig(self):
        command = CMD_SET_CONFIG
        #command += b'\x00'
        config1Bitfield = 0x00
        config2Bitfield = 0x00
        if (self.rxInvert):
            config1Bitfield |= 0x01
        if (self.txInvert):
            config1Bitfield |= 0x02
        if (self.pttInvert):
            config1Bitfield |= 0x04
        if (self.debug):
            config1Bitfield |= 0x10
        if (not self.duplex):
            config1Bitfield |= 0x80

        if (self.dcBlock):
            config2Bitfield |= 0x01
        if (self.cosLockout):
            config2Bitfield |= 0x04
        if (self.dmrEnabled):
            config2Bitfield |= 0x02
        if (self.p25Enabled):
            config2Bitfield |= 0x08

        command += config1Bitfield.to_bytes(1, "big")
        command += config2Bitfield.to_bytes(1, "big")

        command += self.fdmaPreamble.to_bytes(1, "big")

        command += self.current_state
        command += int(self.rxLevel * 2.55 + 0.5).to_bytes(1, 'big')
        command += int(self.cwidLevel * 2.55 + 0.5).to_bytes(1, 'big')
        command += self.dmrColorCode.to_bytes(1, "big")
        command += self.dmrRxDelay.to_bytes(1, "big")
        command += int((self.p25Nac >> 4) & 0xFF).to_bytes(1, "big")
        command += int((self.p25Nac << 4) & 0xF0).to_bytes(1, "big")

        command += int(self.dmrTxLevel * 2.55 + 0.5).to_bytes(1, 'big')
        command += int(self.p25TxLevel * 2.55 + 0.5).to_bytes(1, 'big')

        command += int(self.txDCOffset + 128).to_bytes(1, "big")
        command += int(self.rxDCOffset + 128).to_bytes(1, "big")

        self._send(command)

    def keyRadio(self):
        command = CMD_CAL_DATA + b'\x01'
        self._send(command)
    
    def unkeyRadio(self):
        command = CMD_CAL_DATA + b'\x00'
        self._send(command)

    def _send(self, data):
        packet = b''
        #print("Incoming length: {}".format(len(data)))
        packetLen = int(len(data) + 2).to_bytes(1, "big")
        packet += DVM_FRAME_START
        packet += packetLen
        packet += data
        self._serialPort.reset_input_buffer()
        #print("Sending {}".format(packet))
        self._serialPort.write(packet)

    def _receive(self):
        t_end = time.time() + 1
        reply = b''
        packetLen = 0
        hasStart = False
        hasLen = False
        while time.time() < t_end:
            b = self._serialPort.read(1)
            #print("Got {}".format(b))
            #if it's blank, retry
            if (b == b''):
                break
            else:
                if (hasStart and not hasLen):
                    # got the start byte, now we need to get length
                    # subtract first two length bytes
                    packetLen = int.from_bytes(b, "big") - 2
                    hasLen = True
                    reply += b
                elif (hasStart and hasLen):
                    # add existing byte to reply and deduct from remaining length
                    reply += b
                    packetLen -= 1
                    # have start and length, let's read it out
                    while (packetLen > 0):
                        b = self._serialPort.read(1)
                        #print("Got data {}".format(b))
                        reply += b
                        packetLen -= 1
                    break
                else:
                    if (b == DVM_FRAME_START):
                        hasStart = True
                    else:
                        raise Exception("Expected frame start but did not receive it")
        #print(reply)
        return reply