from .Tests import TXReferenceOscillator, TXPortablePower, TXDeviation
import logging
from .interface import MotorolaAstro25
import time
from datetime import datetime
import subprocess
import os
import signal

AVAILABLE_TESTS =  [TXReferenceOscillator.testTxReferenceOscillator,
                    TXPortablePower.testTxPortablePower,
                    TXDeviation.testTxModBalance]

logger = logging.getLogger(__name__)

WVDIALCONFIG = '''[Dialer Defaults]
Modem = {}
Baud = {}
Init1 = ATZ
Username = 192.168.128.1
Password = test
Phone = 8002
Stupid Mode = 1
New PPPD = yes
PPPD Path = {}
Auto Reconnect = off'''


def dialRadio(config):
    serialPort = config['port']
    baud = config['baud']
    wvdialPath = config['wvdialPath']
    pppdPath = config['pppdPath']
    wvdialConfig = WVDIALCONFIG.format(serialPort, baud, pppdPath)

    wvdialConfigName = 'wvdial.conf'

    c = open(wvdialConfigName, 'w')
    c.write(wvdialConfig)
    c.close()

    print()
    print("Howdy. We're about to start up a PPP dialer. We may need your sudo password for root access.")
    print("If you don't want to deal with this in the future, try adding wvdial to your sudo file.")
    dialProcess = subprocess.Popen(['sudo', wvdialPath, '-C', wvdialConfigName], preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(6)
    #TODO: detect when PPP connects and if it's successful
    return dialProcess

def undialRadio(process):
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)

def performTests(testList, instrument, config):
    serialPort = config['port']
    baud = config['baud']
    ipAddr = '192.168.128.1'
    logger.info("Connecting to radio at {}".format(serialPort))
    dialProcess = dialRadio(config)
    logger.info("PPP connection online; connecting to {}".format(ipAddr))
    radio = MotorolaAstro25(ipAddr)

    try:
        radio.connect()
        logger.info("Entering service mode")
        radio.enterServiceMode()
    except Exception as e:
        dialProcess.terminate()
        instrument.disconnect()
        logger.error("Error connecting to radio.")
        logger.debug(e)
        return

    startTime = time.time()
    report = "-------- Test Report for {} --------\n\n".format(radio.serialNumber)
    report+= "Tested on {}\n".format(datetime.now())
    report+= "Serial: {}\tModel: {}\n".format(radio.serialNumber, radio.modelNumber)
    report+= "Firmware: {}\n".format(radio.firmwareVersion)
    report+= "DSP: {}\tSecure: {}\n".format(radio.dspVersion, radio.secureVersion)
    report+= "Algs: {}\n".format(radio.secureAlgs)
    report += "\n"

    try:
        logger.info("Performing tests...")
        for test in testList:
            logger.info("Beginning {}".format(test.name))
            currTest = test(radio, instrument)

            if (currTest.isRadioEligible()):
                try:
                    report += '--- {} ---\n'.format(currTest.name)
                    currTest.setup()
                    currTest.performTest()
                    #currTest.performAlignment()
                    currTest.tearDown()
                    report += currTest.report
                except Exception as e:
                    logger.error('Test {} failed.'.format(currTest.name))
                    logger.debug(e)
            else:
                logger.error("Test {} does not support your radio.".format(currTest.name))

    except Exception as e:
        logger.error("Error tuning radio.")
        logger.debug(e)
    finally:
        ts = time.strftime('%M:%S', time.gmtime(time.time()-startTime))
        report += "Tests done in {}\n".format(ts)
        print(report)
        radio.resetRadio()
        radio.disconnect()
        dialProcess.terminate()
        instrument.disconnect()