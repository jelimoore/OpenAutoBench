
from abc import abstractmethod

class AutoTest():
    @abstractmethod
    def isRadioEligible(self):
        '''Method for connecting to the test instrument and setting any necessary options'''
        pass

    @abstractmethod
    def setup(self):
        '''Method for disconnecting from the test instrument and cleaning up'''
        pass

    @abstractmethod
    def performTest(self):
        '''Method for generating an RF signal at the specified frequency and amplitude'''
        pass

    @abstractmethod
    def performAlignment(self):
        '''Method for measuring broadband power at the specified frequency'''
        pass

    @abstractmethod
    def tearDown(self):
        '''Method for measuring RF frequency error at the specified frequency'''
        pass