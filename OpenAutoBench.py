from instruments.HPIB.interface import HPIBInterface
import time
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)-8s:%(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
TRBO_ENABLED = False

VERSION = "0.0.1"

def genMenu(header, options):
    selections = []

    while True:
        print()
        print('---- {} ----'.format(header))
        for option, text in options.items():
            selections.append(option)
            print('{}. {}'.format(option, text))
        
        result = None
        try:
            result = int(input("Choose: "))
        except:
            pass

        if (result not in selections):
            print("Invalid selection. Try again.")
        else:
            return result

try:
    import trbo_keys
    TRBO_ENABLED = True
except ImportError:
    import trbo_keys_sample
    logger.warning("Could not find MotoTRBO keys to import. Make sure you renamed the file to trbo_keys.py and the syntax is correct. MotoTRBO tuning will be unavailable.")

logger.info("OpenAutoBench version {} starting up".format(VERSION))

def setupInstrument():
    try:
        instrument = HPIBInterface('/dev/ttyACM0', 14)
        instrument.connect()
        time.sleep(0.5)
        return instrument
    except Exception as e:
        logger.critical("Failure connecting to instrument. Exiting.")
        logger.debug(e)
        exit(1)

def testXPR():
    instrument = setupInstrument()
    try:
        import radios.MotorolaXPR as XPR
        from radios.MotorolaXPR.Tests import TXDeviation
    except ImportError as e:
        logger.critical("Error importing MotoTRBO libraries")
        logger.debug(e)

    ipAddr = '192.168.10.1'

    logger.info("Available tests: {}".format(XPR.AVAILABLE_TESTS))
    #selectedTests = [TXDeviation.testTxModBalance]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = XPR.AVAILABLE_TESTS
    XPR.performTests(selectedTests, instrument, trbo_keys.KEYS, trbo_keys.DELTA, trbo_keys.INDEX, ipAddr)
    

def testAPX():
    ipAddr = '192.168.128.1'
    instrument = setupInstrument()
    try:
        import radios.MotorolaAPX as APX
        from radios.MotorolaAPX.Tests import TXPortablePower
    except ImportError as e:
        logger.critical("Error importing APX libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format(APX.AVAILABLE_TESTS))
    #selectedTests = [TXPortablePower.testTxPortablePower]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = APX.AVAILABLE_TESTS
    APX.performTests(selectedTests, instrument, ipAddr)

def testDVMProject():
    serialPort = '/dev/ttyUSB0'
    instrument = setupInstrument()
    try:
        import radios.DVMProject as DVM
        #from radios.MotorolaAPX.Tests import TXPortablePower
    except ImportError as e:
        logger.critical("Error importing libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format([DVM.AVAILABLE_TESTS]))
    #selectedTests = [TXPortablePower.testTxPortablePower]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = DVM.AVAILABLE_TESTS
    DVM.performTests(selectedTests, instrument, serialPort)

def testRadio():
    menu = {1: "Motorola XPR", 2: "Motorola APX", 4: "DVMProject", 9: "Exit"}
    selection = genMenu('Testing', menu)
    if (selection == 1):
        if (TRBO_ENABLED):
            testXPR()
        else:
            print("TRBO tuning not enabled. Check your keys.")
    elif (selection == 2):
        testAPX()
    elif (selection == 4):
        testDVMProject()
    elif (selection == 9):
        return

# main program
while True:
    menu = {}
    menu[1] = 'Test Radio'
    menu[2] = 'About'
    menu[9] = 'Exit'

    selection = genMenu('Welcome', menu)
    if (selection == 1):
        testRadio()
    elif (selection == 2):
        print("OpenAutoBench version {}".format(VERSION))
    elif (selection == 9):
        print("Bye")
        break