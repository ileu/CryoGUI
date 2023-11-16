import logging
import time
import warnings

from PyQt5.QtCore import QObject, pyqtSignal

logger = logging.getLogger(__name__)


# TODO: check if this needs to be removed
class ClosedLoopController(QObject):
    statusUpdated = pyqtSignal(str)
    modeUpdated = pyqtSignal(str)
    measuredCapacity = pyqtSignal(float)
    valuesUpdated = pyqtSignal(list)
    lockUI = pyqtSignal(bool)

    def __init__(self, axis=None, parent=None):
        warnings.warn("DO NOT USE THIS CONTROLLER")
        super().__init__(parent)
        self.axis = axis
        self.activated = False

    def toggle_activation(self, b: bool):
        self.activated = b

    def measure_capacity(self):
        logger.info("Measuring Capacity")
        self.statusUpdated.emit("Measuring Capacity")
        self.lockUI.emit(False)
        self.update_mode("cap")
        # wait for the measurement to finish
        time.sleep(1)
        # ask if really finished
        self.axis.ask("capw")

        capacity = self.axis.capacity

        self.update_mode("gnd")
        logger.info(f"Measured capacity {capacity} nF")
        self.measuredCapacity.emit(capacity)
        self.lockUI.emit(True)
        self.statusUpdated.emit("Ready")

    def update_mode(self, mode: str = None):
        if mode is None:
            mode = self.axis.mode
        else:
            self.axis.mode = mode
        self.modeUpdated.emit(mode.upper())

    def update_values(self):
        voltage = self.axis.voltage
        frequency = self.axis.frequency
        offset = self.axis.offset_voltage

        self.valuesUpdated.emit([voltage, frequency, offset])
