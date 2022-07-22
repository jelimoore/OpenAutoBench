import time
import logging
import yaml
from yaml.loader import SafeLoader

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s %(module)-8s:%(levelname)-8s %(message)s', level=logging.DEBUG, datefmt='%Y-%m-%d %H:%M:%S')
TRBO_ENABLED = False

VERSION = "0.0.1"
CONFIG = None


try:
    with open('config.yml', 'r') as f:
        CONFIG = list(yaml.load_all(f, Loader=SafeLoader))[0]
except:
    raise Exception("Error opening config file. Does config.yml exist?")

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

def setupInstrument():
    try:
        instrument = None
        instConfig = CONFIG['instrument']

        instProtocol = instConfig['protocol']
        instInterface = instConfig['interface']
        ipAddress = instConfig['ipAddr']
        ipPort = instConfig['ipPort']
        serialPort = instConfig['serialPort']
        baud = int(instConfig['baud'])
        gpibAddr = int(instConfig['gpibAddress'])

        if (instProtocol == 'gpib' and instInterface == 'serial'):
            from instruments.GPIB.interface import GPIBSerialInterface
            instrument = GPIBSerialInterface(serialPort, gpibAddr, baud=baud)

        if (instProtocol == 'gpib' and instInterface == 'tcp'):
            from instruments.GPIB.interface import GPIBTCPInterface
            instrument = GPIBTCPInterface(ipAddress, ipPort, gpibAddress)

        if (instProtocol == 'scpi' and instInterface == 'serial'):
            from instruments.SCPI.interface import SCPISerialInterface
            instrument = SCPISerialInterface(serialPort, baud)

        if (instProtocol == 'scpi' and instInterface == 'tcp'):
            from instruments.SCPI.interface import SCPITCPInterface
            instrument = SCPITCPInterface(ipAddress, ipPort)

        if (instrument is None):
            raise Exception("Unsupported instrument protocol/interface combination: {}, {}".format(instProtocol, instInterface))
        instrument.connect()
        time.sleep(0.2)
        info = instrument.getInfo()
        if (info is None or info == ''):
            raise Exception("Instrument did not respond")
        logger.info("Connected to test set - {}".format(info))
        #time.sleep(0.5)
        return instrument
    except Exception as e:
        logger.critical("Failure connecting to instrument. Exiting.")
        logger.debug(e)
        exit(1)

def testXPR(align=False):
    xprConfig = CONFIG['radios']['trbo']
    ipAddr = xprConfig['ipAddress']
    try:
        import radios.MotorolaXPR as XPR
        from radios.MotorolaXPR.Tests import TXDeviation
    except ImportError as e:
        logger.critical("Error importing MotoTRBO libraries")
        logger.debug(e)

    authConfig = xprConfig['auth']
    keys = authConfig['keys']
    delta = authConfig['delta']
    index = authConfig['index']

    logger.info("Available tests: {}".format(XPR.AVAILABLE_TESTS))
    #selectedTests = [TXDeviation.testTxModBalance]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = XPR.AVAILABLE_TESTS
    instrument = setupInstrument()
    XPR.performTests(selectedTests, instrument, keys, delta, index, ipAddr, align=align)
    

def testAPX(align=False):
    apxConfig = CONFIG['radios']['apx']
    ipAddr = apxConfig['ipAddress']
    try:
        import radios.MotorolaAPX as APX
        from radios.MotorolaAPX.Tests import TXPortablePower
    except ImportError as e:
        logger.critical("Error importing APX libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format(APX.AVAILABLE_TESTS))
    #selectedTests = [TXPortablePower.testTxPortablePower]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = APX.AVAILABLE_TESTS
    instrument = setupInstrument()
    APX.performTests(selectedTests, instrument, ipAddr, align=align)

def testAstro25(align=False):
    astro25Config = CONFIG['radios']['astro25']
    try:
        import radios.MotorolaAstro25 as A25
    except ImportError as e:
        logger.critical("Error importing Astro25 libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format(A25.AVAILABLE_TESTS))
    #selectedTests = [TXPortablePower.testTxPortablePower]  # TXMeasuredPower.testTxMeasuredPower, TXReferenceOscillator.testTxReferenceOscillator
    selectedTests = A25.AVAILABLE_TESTS
    instrument = setupInstrument()
    A25.performTests(selectedTests, instrument, astro25Config, align=align)

def testDVMProject(align=False):
    DVMConfig = CONFIG['radios']['dvmproject']
    serialPort = DVMConfig['port']
    try:
        import radios.DVMProject as DVM
    except ImportError as e:
        logger.critical("Error importing libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format([DVM.AVAILABLE_TESTS]))
    selectedTests = DVM.AVAILABLE_TESTS
    instrument = setupInstrument()
    DVM.performTests(selectedTests, instrument, serialPort, align=align)

def testQuantar(align=False):
    QuantarConfig = CONFIG['radios']['quantar']
    try:
        import radios.MotorolaQuantar as Quantar
    except ImportError as e:
        logger.critical("Error importing libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format([Quantar.AVAILABLE_TESTS]))
    selectedTests = Quantar.AVAILABLE_TESTS
    instrument = setupInstrument()
    Quantar.performTests(selectedTests, instrument, QuantarConfig, align=align)

def testMTR2k(align=False):
    MTR2kConfig = CONFIG['radios']['mtr2k']
    try:
        import radios.MotorolaMTR2k as MTR2k
    except ImportError as e:
        logger.critical("Error importing libraries")
        logger.debug(e)

    logger.info("Available tests: {}".format([MTR2k.AVAILABLE_TESTS]))
    selectedTests = MTR2k.AVAILABLE_TESTS
    instrument = setupInstrument()
    MTR2k.performTests(selectedTests, instrument, MTR2kConfig, align=align)

def testRadio(align=False):
    menu = {1: "Motorola XPR", 2: "Motorola APX", 3: "Motorola Astro25", 4: "DVMProject", 5: "Motorola Quantar", 6: 'MTR2000', 9: "Exit"}
    selection = genMenu('Testing', menu)
    if (selection == 1):
        testXPR(align)
    elif (selection == 2):
        testAPX(align)
    elif (selection == 3):
        testAstro25(align)
    elif (selection == 4):
        testDVMProject(align)
    elif (selection == 5):
        testQuantar(align)
    elif (selection == 6):
        testMTR2k(align)
    elif (selection == 9):
        return

logger.info("OpenAutoBench version {} starting up".format(VERSION))
# main program
while True:
    menu = {}
    menu[1] = 'Test Radio'
    menu[2] = 'Align Radio'
    menu[3] = 'About'
    menu[9] = 'Exit'

    selection = genMenu('Welcome', menu)
    if (selection == 1):
        testRadio()
    elif (selection == 2):
        testRadio(align=True)
    elif (selection == 3):
        print("OpenAutoBench version {}".format(VERSION))
    elif (selection == 9):
        print("Bye")
        break