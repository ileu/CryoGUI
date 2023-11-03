import sys
import time

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStyle,
)

import logging

logger = logging.getLogger(__name__)

push_button_style = (
    "QPushButton {border: 2px solid black; padding-bottom: 2px; "
    "border-radius: 5px; font-size: 20px;}"
    "QPushButton:hover {background-color: rgb(228,241,251); }"
    "QPushButton:pressed {background-color: rgb(204,228,247); }"
    "QPushButton:disabled {background-color: rgb(200,200,200); }"
    "QPushButton:checked {background-color: rgb(150,159,161); }"
)
line_edit_stale_small = (
    "QLineEdit { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 16px;}"
    "QLineEdit:disabled { background-color: rgb(200,200,200); }"
)

line_edit_style_large = (
    "QLineEdit { background-color: white; border: 2px solid black; font-size: 25px;}"
    "QLineEdit:disabled { background-color: rgb(200,200,200); }"
)


class IncrementWidget(QWidget):
    valueChanged = QtCore.pyqtSignal(float, str)

    def __init__(
        self, parent: QWidget = None, title: str = "TEST", unit: str = "", **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.title = QLabel(title + unit)
        self.input = QLineEdit()
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("-")

        self._callOnValueChanged = None

        self.initUI()

    def initUI(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.title.setContentsMargins(0, 0, 0, 0)

        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.setContentsMargins(0, 0, 0, 0)
        self.input.setStyleSheet(line_edit_style_large)
        self.input.setFixedSize(65, 40)
        self.input.setValidator(QIntValidator(bottom=0))
        self.input.setPlaceholderText("0")

        self.plus_button.setStyleSheet(
            "QPushButton { border: 2px solid black; "
            "border-top-left-radius: 5px;  border-bottom-left-radius: 5px; "
            "font-size: 32px; text-align: center; padding-bottom: 5px } "
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.plus_button.setFixedSize(24, 40)
        self.plus_button.clicked.connect(self.incrementValue)
        self.plus_button.setContentsMargins(0, 0, 0, 0)

        self.minus_button.setStyleSheet(
            "QPushButton { border: 2px solid black; "
            "border-top-right-radius: 5px;  border-bottom-right-radius: 5px; "
            "font-size: 32px; text-align: center; padding-bottom: 5px}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.minus_button.setFixedSize(24, 40)
        self.minus_button.clicked.connect(self.decrementValue)
        self.minus_button.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(0)

        side_layout = QHBoxLayout()
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.setSpacing(0)

        side_layout.addWidget(self.plus_button, alignment=Qt.AlignmentFlag.AlignRight)
        side_layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.minus_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(side_layout)

        main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def incrementValue(self):
        try:
            incr_number = float(self.input.text())
        except ValueError:
            return

        self.valueChanged.emit(incr_number, "+")

    def decrementValue(self):
        try:
            incr_number = float(self.input.text())
        except ValueError:
            return

        self.valueChanged.emit(incr_number, "-")

    def activate(self):
        self.plus_button.setEnabled(True)
        self.minus_button.setEnabled(True)
        self.input.setEnabled(True)

    def deactivate(self):
        self.plus_button.setEnabled(False)
        self.minus_button.setEnabled(False)
        self.input.setEnabled(False)


class SetWidget(QWidget):
    valueChanged = QtCore.pyqtSignal(float)

    def __init__(
        self, title="", symbols: int = 7, unit: str = "", bottom=0, top=60, **kwargs
    ):
        super().__init__()
        self.value = 0
        self.symbols = symbols
        self.unit = unit
        self.top = top
        self.bottom = bottom

        self.title = QLabel(f"{title} [{unit}]")
        self.input = QLineEdit()
        self.set_button = QPushButton("Set")

        self._callOnValueChanged = None

        self.initUI()

        self.valueChanged.connect(self.set_input_text)

    def set_input_text(self, text):
        if not isinstance(text, str):
            text = str(text)

        if not self.input.hasFocus():
            self.input.setText(text)

    def initUI(self):
        self.input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input.setStyleSheet(
            line_edit_stale_small
            + "QLineEdit { border-top-right-radius: 0px; border-bottom-right-radius: 0px;}"
        )
        self.input.setFixedSize((self.symbols + 1) * 10, 24)  # +1 because decimal point
        self.input.setValidator(QDoubleValidator(bottom=self.bottom, top=self.top))
        self.input.returnPressed.connect(self.setValue)
        self.input.setPlaceholderText(f"{self.value}"[: self.symbols - 1])
        self.input.setMaxLength(int(self.symbols))

        self.set_button.setStyleSheet(
            push_button_style
            + "QPushButton { border-top-left-radius: 0px; border-bottom-left-radius: 0px;}"
        )
        self.set_button.setFixedSize(50, 24)
        self.set_button.clicked.connect(self.setValue)

        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignLeft)
        control_layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignLeft)
        control_layout.addWidget(self.set_button, alignment=Qt.AlignmentFlag.AlignLeft)
        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(main_layout)

    def setValue(self, value=None):
        if not value:
            try:
                if self.input.hasAcceptableInput():
                    value = float(self.input.text())
                else:
                    return
            except ValueError:
                logger.warning(f"{self.title} failed to set value")

        self.value = value
        self.valueChanged.emit(value)

    def activate(self):
        self.input.setEnabled(True)
        self.set_button.setEnabled(True)

    def deactivate(self):
        self.input.setEnabled(False)
        self.set_button.setEnabled(False)


class ControlBar(QWidget):
    def __init__(self, title="Title", off_mode="OFF", on_mode="ON"):
        super().__init__()

        self.title_label = QLabel(title)
        self.status_label = QLabel("Status: Disconnected")

        self.off_mode = off_mode
        self.on_mode = on_mode

        self.mode_button = QPushButton(self.off_mode)

        self.active_button = QPushButton()

        self.capacity_button = QPushButton("Cap: NaN")

        self.initUI()

    def initUI(self):
        self.active_button.setCheckable(True)
        self.active_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.active_button.setFixedSize(30, 20)
        self.active_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 0px; "
            "border-radius: 5px; font-size: 16px;"
            "background-color: rgb(255,75,50);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.active_button.clicked.connect(self.toggle_activation)

        self.mode_button.setCheckable(True)
        self.mode_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 16px; font-weight: bold;"
            "background-color: rgb(180,180,255);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.mode_button.setFixedSize(40, 20)

        self.capacity_button.setStyleSheet(
            push_button_style
            + "QPushButton {font-size: 12px; border: 1px solid gray; padding-bottom: 0px;}"
        )

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.capacity_button)
        text_layout.addStretch()
        text_layout.addWidget(self.status_label)
        text_layout.addWidget(self.active_button)
        text_layout.addWidget(self.mode_button)
        main_layout.addLayout(text_layout)

        self.setLayout(main_layout)

    def set_mode(self, mode):
        if mode == self.off_mode:
            self.mode_button.setText(mode)
            self.mode_button.setChecked(False)
        else:
            self.mode_button.setText(mode)
            self.mode_button.setChecked(True)

    def set_capacity(self, capacity: float):
        logger.debug(f"Set capacity to {capacity}")
        self.capacity_button.setText(f"{int(capacity)}")

    @QtCore.pyqtSlot(bool)
    def toggle_activation(self, movable):
        if movable:
            self.active_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.active_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    def activate(self):
        self.mode_button.setEnabled(True)
        self.active_button.setEnabled(True)
        self.capacity_button.setEnabled(True)

    def deactivate(self):
        self.mode_button.setEnabled(False)
        self.active_button.setEnabled(False)
        self.capacity_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SetWidget(title="HALLO", unit="m", symbols=7)
    window.show()
    time.sleep(1)
    window.value = 5
    print("DONE")
    sys.exit(app.exec())
