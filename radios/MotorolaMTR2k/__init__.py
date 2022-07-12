from .Tests import TXReferenceOscillator, TXDeviation, TXPower, RXRSSI
import logging
from .interface import MotorolaQuantar
import time
from datetime import datetime
import subprocess
import os
import signal

AVAILABLE_TESTS =  [TXReferenceOscillator.testTxReferenceOscillator,
                    TXDeviation.testTxModBalance]

logger = logging.getLogger(__name__)

def performTests(testList, instrument, config):
    serialPort = config['port']
    baud = config['baud']
    logger.info("Connecting to radio at {}".format(serialPort))
    radio = MotorolaQuantar(serialPort, baud=baud)

    try:
        radio.connect()
        logger.info("Setting access disable")
        radio.accessDisable()
    except Exception as e:
        instrument.disconnect()
        logger.error("Error connecting to radio.")
        logger.debug(e)
        return

    startTime = time.time()
    report = "-------- Test Report for {} --------\n\n".format(radio.stationName)
    report+= "Tested on {}\n".format(datetime.now())
    report+= "Serial: {}\tCodeplug: {}\n".format(radio.serialNumber, radio.codeplugVersion)
    report+= "Firmware: {}\n".format(radio.firmwareVersion)
    report+= "Hardware: {}\n".format(radio.hardware)
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
        radio.accessEnable()
        radio.reset()
        radio.disconnect()
        instrument.disconnect()