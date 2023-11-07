import logging
import os

from PyQt5.QtCore import Qt, QThread, pyqtSlot
from PyQt5.QtCore import pyqtSignal
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
from pymeasure.instruments.attocube.anc300 import Axis

from src.controller.openloopcontroller import OpenLoopController
from src.dummies.dummies import DummyOpenLoopAxis
from src.view.utilitywidgets import (
    SetWidget,
    IncrementWidget,
    push_button_style,
    ControlBar,
)

logger = logging.getLogger(__name__)


def scream():
    logger.info("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")


class OpenLoopWidget(QFrame):
    updateValues = pyqtSignal()
    stepAxis = pyqtSignal(float, str)

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
        self.cmove_down_button = QPushButton(">>")
        self.cmove_up_button = QPushButton("<<")

        if axis is None:
            self.controller = OpenLoopController()
            self.deactivate()
        else:
            self.controller = OpenLoopController(axis=axis)

        self.controller_thread = QThread()
        self.controller_thread.start()
        self.controller.moveToThread(self.controller_thread)

        self.controller.lockUI.connect(self.toggle_activation)

        self.initUI()

        self.controller.statusUpdated.connect(self.control_bar.status_label.setText)
        self.controller.statusUpdated.emit("Disconnected")

        self.control_bar.mode_button.clicked.connect(
            lambda: self.controller.update_mode("gnd")
        )

        self.control_bar.capacity_button.clicked.connect(
            self.controller.measure_capacity
        )
        self.controller.measuredCapacity.connect(self.control_bar.set_capacity)

        self.lock_button.clicked.connect(self.optimize_button.setEnabled)
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

        self.cmove_down_button.setStyleSheet(push_button_style)
        self.cmove_down_button.setFixedSize(40, 20)

        self.cmove_up_button.setStyleSheet(push_button_style)
        self.cmove_up_button.setFixedSize(40, 20)

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
            self.cmove_up_button, alignment=Qt.AlignmentFlag.AlignRight
        )
        cmove_layout.addWidget(
            self.cmove_down_button, alignment=Qt.AlignmentFlag.AlignLeft
        )

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

    def refresh_values(self, values: list):
        self.voltage_widget.setValue(values[0])
        self.frequency_widget.setValue(values[1])
        self.offset_widget.setValue(values[2])

    def connect_axis(self, axis: Axis):
        self.controller.axis = axis

        self.controller.modeUpdated.connect(self.control_bar.set_mode)
        self.controller.valuesUpdated.connect(self.refresh_values)

        self.voltage_widget.valueChanged.connect(
            lambda value: self.controller.set_value(value, "voltage")
        )
        self.frequency_widget.valueChanged.connect(
            lambda value: self.controller.set_value(value, "frequency")
        )
        self.offset_widget.valueChanged.connect(
            lambda value: self.controller.set_value(value, "offset_voltage")
        )
        self.step_widget.valueChanged.connect(self.controller.step_axis)
        self.cmove_down_button.pressed.connect(
            lambda: self.controller.step_axis(1, "up")
        )
        # self.cmove_down_button.released.connect(
        #     lambda: self.controller.step_axis(1, "up")
        # )
        self.cmove_up_button.pressed.connect(
            lambda: self.controller.step_axis(1, "down")
        )
        # self.cmove_up_button.released.connect(
        #     lambda: self.controller.step_axis(1, "down")
        # )
        self.controller.update_values()
        self.activate()
        self.controller.statusUpdated.emit("Ready")

    def connect_keys(self, up_key, down_key):
        if self.controller.axis is None:
            return
        self.cmove_down_button.setShortcut(down_key)
        self.cmove_up_button.setShortcut(up_key)

    def toggle_activation(self, toggle):
        if toggle:
            self.activate()
        else:
            self.deactivate()

    def activate(self):
        logger.debug(f"Activating {self.title}")
        self.control_bar.activate()
        self.voltage_widget.activate()
        self.frequency_widget.activate()
        self.offset_widget.activate()
        self.step_widget.activate()
        self.cmove_down_button.setEnabled(True)
        self.cmove_up_button.setEnabled(True)
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
        self.cmove_down_button.setEnabled(False)
        self.cmove_up_button.setEnabled(False)
        self.lock_button.setEnabled(False)
        self.optimize_button.setEnabled(False)


def main():
    logging.basicConfig(level=logging.INFO)
    app = QApplication([])
    # olw = OpenLoopWidget(axis=DummyAxis(), title="Test", lock_optimize_on_start=False)
    olw = OpenLoopWidget(lock_optimize_on_start=True)
    olw.connect_axis(DummyOpenLoopAxis())
    # olw.controller.start_refresh_timer()
    olw.show()
    app.exec()


if __name__ == "__main__":
    main()
    # test = OpenLoopController(axis=DummyOpenLoopAxis())
    # test.measure_capacity()
