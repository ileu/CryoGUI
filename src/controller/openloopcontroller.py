import time

from PyQt5.QtCore import QObject, pyqtSignal, QTimer

import logging

logger = logging.getLogger(__name__)


class OpenLoopController(QObject):
    statusUpdated = pyqtSignal(str)
    modeUpdated = pyqtSignal(str)
    measuredCapacity = pyqtSignal(float)
    valuesUpdated = pyqtSignal(list)
    lockUI = pyqtSignal(bool)

    def __init__(self, axis=None, parent=None):
        super().__init__(parent)
        self.axis = axis
        self.refresh_timer = None

    # def __getattribute__(self, item):
    #     if item != "axis" and self.axis is None:
    #         print("Cant do a thing with no axis")
    #         print("Set axis first")
    #         return None
    #
    #     return super().__getattribute__(item)

    def start_refresh_timer(self):
        if self.refresh_timer is None:
            self.refresh_timer = QTimer(self)

        self.refresh_timer.timeout.connect(self.refresh)

        self.refresh_timer.start(500)

    def stop_refresh_timer(self):
        self.refresh_timer.stop()

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

    def set_value(self, value: float, name: str):
        logger.debug(f"Set {name} to {value}")
        setattr(self.axis, name, value)

    def step_axis(self, value: float, direction: str):
        logger.debug(f"Step {direction} by {value}")
        self.statusUpdated.emit("Stepping")
        if self.axis.offset_voltage != 0:
            self.update_mode("stp+")
        else:
            self.update_mode("stp")

        try:
            if direction in ["up", "+"]:
                self.axis.stepu = value
            elif direction in ["down", "-"]:
                self.axis.stepd = value
            else:
                logger.warning(f"Invalid direction {direction}")
            self.statusUpdated.emit("Ready")
        except Exception as e:
            logger.warning(f"Error stepping axis: {e}")

    def refresh(self):
        self.update_mode()
        self.update_values()

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
