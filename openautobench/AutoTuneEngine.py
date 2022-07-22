
class AutoTuneEngine():
    def __init__(self, measureCallback, setSoftpotCallback, beginningSoftpot, beginningMeasurement, targetMeasurement, tolerance=0.05):
        self._measureFunc = measureCallback
        self._setSpFunc = setSoftpotCallback
        self._bsp = float(beginningSoftpot)
        self._csp = self._bsp
        self._bmeas = float(beginningMeasurement)
        self._targetMeas = float(targetMeasurement)
        self._tolerance = 0.05
        self.report = ''

    def tune(self):
        # get initial measurement to find stepping
        stepping = 0
        self._setSpFunc(self._bsp - 5)
        stepping = (self._measureFunc() - self._bmeas) / 5
        #print("Found stepping {}".format(stepping))

        numSteps = int((self._bmeas - self._targetMeas)/ stepping)
        self._csp = self._bsp + numSteps
        #print("Going {} steps to {}".format(numSteps, self._csp))
        self._setSpFunc(self._csp)
        meas = self._measureFunc()
        #print("New measurement: {}".format(meas))

        #TODO: nudge up and down to find final value