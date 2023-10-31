import os
import time

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)
from PyQt5.QtCore import pyqtSignal
from pymeasure.instruments.attocube.anc300 import Axis

from src.dummies.dummies import DummyOpenLoopAxis
from src.view.utilitywidgets import (
    SetWidget,
    IncrementWidget,
    push_button_style,
    ControlBar,
)

import logging

logger = logging.getLogger(__name__)


def scream():
    logger.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


class OpenLoopController(QRunnable):
    statusUpdated = pyqtSignal(str)
    measuredCapacity = pyqtSignal(float)
    valuesUpdated = pyqtSignal(list)
    lockUI = pyqtSignal(bool)

    def __init__(self, axis=None, parent=None):
        super().__init__(parent)
        self.axis = axis

    def __getattribute__(self, item):
        if item != "axis" and self.axis is None:
            print("Cant do a thing with no axis")
            print("Set axis first")
            return None

        return super().__getattribute__(item)

    def measure_capacity(self):
        logger.info("Measuring Capacity")
        self.statusUpdated.emit("Measuring Capacity")
        self.lockUI.emit(True)
        self.axis.mode = "cap"
        # wait for the measurement to finish
        time.sleep(1)
        # ask if really finished
        self.axis.ask("capw")

        capacity = self.axis.capacity

        logger.info(f"Measured capacity {capacity} nF")
        self.measuredCapacity.emit(capacity)
        self.lockUI.emit(False)
        self.statusUpdated.emit("Ready")

    def step_axis(self, value: float, direction: str):
        logger.debug(f"Step {direction} by {value}")
        if self.axis.offset_voltage != 0:
            self.axis.mode = "stp+"
            self.statusUpdated.emit("stp")
        else:
            self.axis.mode = "stp"
            self.statusUpdated.emit("stp")

        try:
            if direction == "up":
                self.axis.stepu = value
            elif direction == "down":
                self.axis.stepd = value
            else:
                logger.warning(f"Invalid direction {direction}")
        except Exception as e:
            logger.warning(f"Error stepping axis: {e}")

    def update_values(self):
        mode = self.axis.mode

        voltage = self.axis.voltage
        frequency = self.axis.frequency
        offset = self.axis.offset_voltage

        self.valuesUpdated.emit([mode.upper(), voltage, frequency, offset])


class OpenLoopWidget(QFrame):
    def __init__(
        self,
        parent: QWidget = None,
        axis: Axis = None,
        title: str = "Quantity",
        lock_optimize_on_start: bool = True,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.title = title

        self.control_bar = ControlBar(off_mode="GND")
        self.control_bar.title_label.setText(title)

        self.voltage_widget = SetWidget(title="Voltage", symbols=8, unit="V", top=60)
        self.frequency_widget = SetWidget(
            title="Frequency", symbols=8, unit="Hz", top=900
        )
        self.offset_widget = SetWidget(title="Offset", symbols=8, unit="V", top=90)

        self.step_widget = IncrementWidget(title="Step")

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setEnabled(False)
        self.lock_button = QPushButton()
        self.cmover_button = QPushButton(">>")
        self.cmovel_button = QPushButton("<<")

        if axis is None:
            self.controller = OpenLoopController()
            self.deactivate()
        else:
            self.controller = OpenLoopController(axis=axis)

        self.initUI()

        self.controller.statusUpdated.connect(self.control_bar.status_label.setText)
        self.controller.statusUpdated.emit("Disconnected")

        self.grounded = False
        self.movable = False

        self.lock_button.clicked.connect(self.optimize_button.setEnabled)
        self.controller.measuredCapacity.connect(
            lambda x: self.control_bar.capacity_button.setText(f"{int(x)} nF")
        )

        self.lock_path = os.path.join(os.path.dirname(__file__), r"..\icons")

        self.on_lock_toggled(not lock_optimize_on_start)
        if not lock_optimize_on_start:
            self.lock_button.click()

    def initUI(self):
        self.setObjectName("OpenLoopWidget")
        self.setStyleSheet("#OpenLoopWidget {border-top: 3px solid darkgray;}")
        self.setContentsMargins(0, 0, 0, 0)
        self.optimize_button.setStyleSheet(push_button_style)
        self.optimize_button.setFixedSize(100, 30)
        self.optimize_button.clicked.connect(scream)

        self.lock_button.setStyleSheet(push_button_style)
        self.lock_button.setFixedSize(30, 30)
        self.lock_button.setCheckable(True)
        self.lock_button.toggled.connect(self.on_lock_toggled)

        self.cmover_button.setStyleSheet(push_button_style)
        self.cmover_button.setFixedSize(40, 20)

        self.cmovel_button.setStyleSheet(push_button_style)
        self.cmovel_button.setFixedSize(40, 20)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)

        main_layout.addWidget(self.control_bar)
        control_layout = QGridLayout()
        control_layout.setSpacing(5)
        main_layout.addLayout(control_layout)

        control_layout.addWidget(self.voltage_widget, 0, 0)
        control_layout.addWidget(self.frequency_widget, 1, 0)
        control_layout.addWidget(self.offset_widget, 0, 1)
        optimize_layout = QHBoxLayout()
        optimize_layout.addWidget(
            self.optimize_button, alignment=Qt.AlignmentFlag.AlignCenter
        )
        optimize_layout.addWidget(self.lock_button)
        control_layout.addLayout(optimize_layout, 1, 1)

        step_layout = QVBoxLayout()
        step_layout.setSpacing(0)
        step_layout.addWidget(self.step_widget, alignment=Qt.AlignmentFlag.AlignLeft)

        cmove_layout = QHBoxLayout()
        cmove_layout.setSpacing(0)
        cmove_layout.addWidget(
            self.cmovel_button, alignment=Qt.AlignmentFlag.AlignRight
        )
        cmove_layout.addWidget(self.cmover_button, alignment=Qt.AlignmentFlag.AlignLeft)

        step_layout.addLayout(cmove_layout)
        control_layout.addLayout(step_layout, 0, 2, 2, 1)

        main_layout.addStretch()

        self.setLayout(main_layout)

    @pyqtSlot(bool)
    def on_lock_toggled(self, toggle):
        if toggle:
            self.lock_button.setIcon(QIcon(self.lock_path + r"\lock.png"))
        else:
            self.lock_button.setIcon(QIcon(self.lock_path + r"\unlock.png"))

    def refresh_values(self):
        pass

    def connect_axis(self, axis: Axis):
        self.controller.axis = axis

        # self.voltage_widget.valueChanged.connect(
        #     lambda value: setattr(self.axis, "voltage", value)
        # )
        # self.frequency_widget.valueChanged.connect(
        #     lambda value: setattr(self.axis, "frequency", value)
        # )
        # self.offset_widget.valueChanged.connect(
        #     lambda value: setattr(self.axis, "offset_voltage", value)
        # )
        # self.step_widget.valueChanged.connect(self.step_axis)
        #
        # self.cmover_button.pressed.connect(lambda: self.step_axis(1, "up"))
        # self.cmover_button.released.connect(lambda: self.step_axis(0, "up"))
        # self.cmovel_button.pressed.connect(lambda: self.step_axis(1, "down"))
        # self.cmovel_button.released.connect(lambda: self.step_axis(0, "down"))

    def activate(self):
        logger.debug(f"Activating {self.title}")
        self.control_bar.activate()
        self.voltage_widget.activate()
        self.frequency_widget.activate()
        self.offset_widget.activate()
        self.step_widget.activate()
        self.cmover_button.setEnabled(True)
        self.cmovel_button.setEnabled(True)
        self.lock_button.setEnabled(True)
        if self.lock_button.isChecked():
            self.optimize_button.setEnabled(True)

    def deactivate(self):
        logger.debug(f"Disabling {self.title}")
        self.control_bar.deactivate()
        self.voltage_widget.deactivate()
        self.frequency_widget.deactivate()
        self.offset_widget.deactivate()
        self.step_widget.deactivate()
        self.cmover_button.setEnabled(False)
        self.cmovel_button.setEnabled(False)
        self.lock_button.setEnabled(False)
        self.optimize_button.setEnabled(False)


def main():
    logging.basicConfig(level=logging.INFO)
    app = QApplication([])
    # olw = OpenLoopWidget(axis=DummyAxis(), title="Test", lock_optimize_on_start=False)
    olw = OpenLoopWidget(axis=DummyOpenLoopAxis(), lock_optimize_on_start=True)
    olw.deactivate()
    olw.activate()
    olw.show()
    app.exec()


if __name__ == "__main__":
    # main()
    test = OpenLoopController(axis=DummyOpenLoopAxis())
    test.measure_capacity()
