from .Tests import TXReferenceOscillator, TXPortablePower, TXDeviation
import logging
from .interface import MotorolaAPX
import time
from datetime import datetime

AVAILABLE_TESTS =  [TXReferenceOscillator.testTxReferenceOscillator,
                    TXPortablePower.testTxPortablePower,
                    TXDeviation.testTxModBalance]

logger = logging.getLogger(__name__)

def performTests(testList, instrument, ipAddr):
    logger.info("Connecting to radio at {}".format(ipAddr))
    radio = MotorolaAPX(ipAddr)

    try:
        radio.connect()
        print("Entering service mode")
        radio.enterServiceMode()
    except Exception as e:
        logger.error("Error connecting to radio.")
        logger.debug(e)
        return

    startTime = time.time()
    report = "-------- Test Report for {} --------\n\n".format(radio.serialNumber)
    report+= "Tested on {}\n".format(datetime.now())
    report+= "Serial: {}\tFirmware: {}\n".format(radio.serialNumber, radio.firmwareVersion)
    report+= "CP: {}\tTuning: {}\n".format(radio.codeplugVersion, radio.tuningVersion)
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
        instrument.disconnect()