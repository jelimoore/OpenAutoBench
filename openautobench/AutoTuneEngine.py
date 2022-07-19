
class AutoTuneEngine():
    def __init__(self, measureCallback, setSoftpotCallback, beginningSoftpot, beginningMeasurement, tolerance=0.05):
        self._measureFunc = measureCallback
        self._setSpFunc = setSoftpotCallback
        self._bsp = beginningSoftpot
        self._bmeas = beginningMeasurement
        self._tolerance = 0.05

    def tune():
        # get initial measurement to find stepping
        stepping = 0
        self._setSpFunc(beginningSoftpot - 10)
        stepping = (self._measureFunc() - self._bmeas) / 10
        print("Found stepping {}".format(stepping))

    '''
    def __init__(self, beginSetting, beginMeas, setMeas):
        self.currentSetting = beginSetting - 5  # current setting/softpot value is 3 steps lower
        self._beginSetting = beginSetting   # beginning setting/softpot value
        self._currentMeasurement = beginMeas    # current measurement
        self._setpointMeasurement = setMeas # desired setpoint
        self._reverseDirection = False  # do we incr the softpot to reduce the measurement?
        self._hasRunOnce = False
        self._step = 0

    def setCurrentMeasurement(self, currMeas):
        deltaStd = self._setpointMeasurement - currMeas
        deltaLast = self._currentMeasurement - currMeas
        #print("Delta from standard: {}, delta from last: {}".format(deltaStd, deltaLast))
        
        if (not self._hasRunOnce):
            self._step = deltaLast / 5
            #print("Estimated step: {}".format(self._step))
            self._hasRunOnce = True
            pass
        
        numSteps = int(deltaStd / self._step)
        #print("Going {} steps".format(numSteps))
        self.currentSetting += numSteps
        #print(self.currentSetting)

        self._currentMeasurement = currMeas
    '''
  