from .Tests import TXReferenceOscillator, TXP25Modulation, TXDMRModulation, RXRSSIPlot
import logging
from .interface import DVMProjectInterface
from .interface import STATE_IDLE
from datetime import datetime
import time


AVAILABLE_TESTS =  [TXReferenceOscillator.testTxReferenceOscillator,
                    TXP25Modulation.testTxP25Modulation,
                    TXDMRModulation.testTxDMRModulation,
                    RXRSSIPlot.testRxRSSIPlot]

logger = logging.getLogger(__name__)

def getFrequency(prompt):
    while True:
        try:
            result = float(input(prompt))
            return result
        except:
            print("Invalid frequency entered. Please try again.")

def performTests(testList, instrument, serialPort, align=False):
    logger.info("Connecting to radio at {}".format(serialPort))
    radio = DVMProjectInterface(serialPort)

    try:
        radio.connect()
        radio.sendRFConfig()
        radio.sendConfig()
    except Exception as e:
        logger.error("Error connecting to radio.")
        logger.debug(e)
        return

    uplink = None
    downlink = None
    if (not radio.isHotspot):
        print()
        print("Howdy. We detected that you're running a repeater.")
        print("We need to know what frequency your repeater is running at.")
        downlink = getFrequency("Please enter your system downlink frequency, in MHz: ")
        uplink = getFrequency("And your uplink frequency, in MHz: ")
        print()
    startTime = time.time()
    report = "-------- Test Report for {} --------\n\n".format(radio.uid)
    report += "Device Type: {}\n".format(("Air Interface", "Hotspot")[radio.isHotspot])
    report += "Tested on {}\n".format(datetime.now())
    report += '\n'

    try:
        logger.info("Performing tests...")
        for test in testList:
            logger.info("Beginning {}".format(test.name))
            currTest = test(radio, instrument, uplink=uplink, downlink=downlink)

            if (currTest.isRadioEligible()):
                try:
                    report += '--- {} ---\n'.format(currTest.name)
                    currTest.setup()
                    currTest.performTest()
                    report += currTest.report
                    currTest.tearDown()
                    report += '\n'
                    time.sleep(1)
                except Exception as e:
                    logger.error('Test {} failed.'.format(currTest.name))
                    logger.debug(e)
            else:
                logger.error("Test {} does not support your radio.".format(currTest.name))
    except Exception as e:
        logger.error("Error tuning hotspot.")
        logger.debug(e)
    finally:
        ts = time.strftime('%M:%S', time.gmtime(time.time()-startTime))
        report += "Tests done in {}\n".format(ts)
        radio.setMode(STATE_IDLE)
        print(report)
        radio.disconnect()
        instrument.disconnect()