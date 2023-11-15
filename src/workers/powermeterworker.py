import time

from PyQt5.QtCore import QObject, pyqtSignal


class PowerMeterWorker(QObject):
    powerMeasured = pyqtSignal(float)

    def __init__(self, power_meter):
        super().__init__()
        self.power_meter = power_meter

    def initialize(self):
        if hasattr(self.power_meter, "instrument"):
            self.power_meter.instrument.waiting = False
        else:
            self.power_meter.waiting = False

    def kill(self):
        if hasattr(self.power_meter, "instrument"):
            self.power_meter.instrument.waiting = True
        else:
            self.power_meter.waiting = True

    def run(self):
        while True:
            if hasattr(self.power_meter, "instrument"):
                if not self.power_meter.instrument.waiting:
                    power = self.power_meter.power_uW
                    self.powerMeasured.emit(power)
                else:
                    time.sleep(2)
            else:
                if not self.power_meter.waiting:
                    power = self.power_meter.power_uW
                    self.powerMeasured.emit(power)
                else:
                    time.sleep(2)
