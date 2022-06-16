from abc import abstractmethod

class InstrumentBase():
    @abstractmethod
    def connect(self, address):
        '''Method for connecting to the test instrument and setting any necessary options'''
        pass

    @abstractmethod
    def disconnect(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        pass

    @abstractmethod
    def generateRFSignal(self, frequency, amplitude):
        '''Method for generating an RF signal at the specified frequency and amplitude'''
        pass

    @abstractmethod
    def measureRFPower(self, frequency):
        '''Method for measuring broadband power at the specified frequency'''
        pass

    @abstractmethod
    def measureRFError(self, frequency):
        '''Method for measuring RF frequency error at the specified frequency'''
        pass