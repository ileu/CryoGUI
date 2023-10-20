import os
import time

from PyQt6.QtCore import Qt, QThread, pyqtSlot
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal
from pymeasure.instruments.attocube.anc300 import Axis

from src.dummies.dummies import DummyClosedLoopAxis
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


class Mover(QThread):
    finished = pyqtSignal()

    def __init__(self, axis: Axis, step: float, direction: str, parent=None):
        super().__init__(parent)
        self.axis = axis
        self.step = step
        self.direction = direction

    def run(self):
        print("running")
        time.sleep(30)
        print("finished")
        self.finished.emit()

    def stop(self):
        self.terminate()


class OpenLoopWidget(QFrame):
    statusUpdated = pyqtSignal(str)

    def __init__(
        self,
        parent: QWidget = None,
        axis: Axis | DummyClosedLoopAxis = None,
        title: str = "Quantity",
        lock_optimize_on_start: bool = True,
        **kwargs,
    ):
        super().__init__(parent, **kwargs)
        self.control_bar = ControlBar()

        self.control_bar.title_label.setText(title)

        self.statusUpdated.connect(self.control_bar.status_label.setText)
        self.statusUpdated.emit("Disconnected")

        self.voltage_widget = SetWidget(title="Voltage", symbols=8, unit="V")
        self.frequency_widget = SetWidget(title="Frequency", symbols=8, unit="Hz")
        self.offset_widget = SetWidget(title="Offset", symbols=8, unit="V")

        self.step_widget = IncrementWidget(title="Step")

        self.optimize_button = QPushButton("Optimize")
        self.optimize_button.setEnabled(False)
        self.lock_button = QPushButton()
        self.cmover_button = QPushButton(">>")
        self.cmovel_button = QPushButton("<<")

        self.grounded = False
        self.movable = False

        self.lock_button.clicked.connect(self.optimize_button.setEnabled)
        self.lock_button.setChecked(lock_optimize_on_start)

        self.lock_path = os.path.join(os.path.dirname(__file__), r"..\icons")

        self.initUI()

        if axis is None:
            self.axis: Axis = None
            self.deactivate()
        else:
            self.axis = axis

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

    def step_axis(self, value: float, direction: str):
        logger.info(f"Step {direction} by {value}")
        try:
            if direction == "up":
                self.axis.stepu(value)
            elif direction == "down":
                self.axis.stepd(value)
            else:
                logger.warning(f"Invalid direction {direction}")
        except Exception as e:
            logger.warning(f"Error stepping axis: {e}")

    def activate(self):
        for widget in self.findChildren(QWidget):
            # if widget == self.optimize_button:
            #     self.optimize_button.setEnabled(not self.locked_optimize)
            #     logger.debug(f"Special enabling {widget}")
            #     continue
            logger.debug(f"Enabling {widget}")
            widget.setEnabled(True)

        self.control_bar.mode_button.setText(self.axis.status)

        self.voltage_widget.valueChanged.connect(
            lambda value: setattr(self.axis, "voltage", value)
        )
        self.frequency_widget.valueChanged.connect(
            lambda value: setattr(self.axis, "frequency", value)
        )

        self.offset_widget.valueChanged.connect(
            lambda value: setattr(self.axis, "offset_voltage", value)
        )
        self.step_widget.valueChanged.connect(self.step_axis)

        self.cmover_button.pressed.connect(lambda: self.step_axis(1, "up"))
        self.cmover_button.released.connect(lambda: self.step_axis(0, "up"))
        self.cmovel_button.pressed.connect(lambda: self.step_axis(1, "down"))
        self.cmovel_button.released.connect(lambda: self.step_axis(0, "down"))

    def deactivate(self):
        for widget in self.findChildren(QWidget):
            if widget == self.optimize_button:
                logger.debug(f"Skipping {widget}")
                continue
            logger.debug(f"Disabling {widget}")
            widget.setEnabled(False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = QApplication([])
    # olw = OpenLoopWidget(axis=DummyAxis(), title="Test", lock_optimize_on_start=False)
    olw = OpenLoopWidget(axis=DummyClosedLoopAxis(), lock_optimize_on_start=False)
    olw.deactivate()
    olw.show()
    app.exec()
