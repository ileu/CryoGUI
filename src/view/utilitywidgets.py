import sys
from typing import Callable

from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QWidget,
    QLineEdit,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QStyle,
)

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
    onValueChanged = QtCore.pyqtSignal(float)

    def __init__(self, parent: QWidget = None, title: str = "TEST", unit: str = "", **kwargs):
        super().__init__(parent, **kwargs)
        self.value = 0.0

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
        self.input.setValidator(QDoubleValidator())
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

        self.value += incr_number

        self.onValueChanged.emit(self.value)

    def decrementValue(self):
        try:
            incr_number = float(self.input.text())
        except ValueError:
            return

        self.value -= incr_number

        self.onValueChanged.emit(self.value)


class SetWidget(QWidget):
    onValueChanged = QtCore.pyqtSignal(float)

    def __init__(self, title="", symbols: int = 7, unit: str = "", **kwargs):
        super().__init__()
        self.value = 0
        self.symbols = symbols
        self.unit = unit

        self.title = QLabel(f"{title} [{unit}]")
        self.input = QLineEdit()
        self.set_button = QPushButton("Set")

        self._callOnValueChanged = None

        self.initUI()

    def initUI(self):
        self.input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input.setStyleSheet(
            line_edit_stale_small
            + "QLineEdit { border-top-right-radius: 0px; border-bottom-right-radius: 0px;}"
        )
        self.input.setFixedSize((self.symbols + 1) * 10, 24)  # +1 because decimal point
        self.input.setValidator(QDoubleValidator())
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

    def setValue(self):
        try:
            self.value = float(self.input.text())
        except ValueError:
            self.value = 0.0

        self.onValueChanged.emit(self.value)


class ControlBar(QWidget):
    def __init__(self, title="Title"):
        super().__init__()

        self.title_label = QLabel(title)
        self.status_label = QLabel("Status: Disconnected")

        self.power_button = QPushButton("OFF")

        self.move_button = QPushButton()

        self.capacity_button = QLabel("Cap: NaN")

        self.powered = False
        self.movable = False

        self.initUI()

    def initUI(self):
        self.move_button.setCheckable(True)
        self.move_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )
        self.move_button.setFixedSize(30, 20)
        self.move_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 0px; "
            "border-radius: 5px; font-size: 16px;"
            "background-color: rgb(255,75,50);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.move_button.clicked.connect(self.toggle_moveable)

        self.power_button.setCheckable(True)
        self.power_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 16px; font-weight: bold;"
            "background-color: rgb(180,180,255);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.power_button.setFixedSize(40, 20)
        self.power_button.clicked.connect(self.toggle_power)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.capacity_button)
        text_layout.addStretch()
        text_layout.addWidget(self.status_label)
        text_layout.addWidget(self.move_button)
        text_layout.addWidget(self.power_button)
        main_layout.addLayout(text_layout)

        self.setLayout(main_layout)

    def toggle_moveable(self):
        self.movable = not self.movable
        if self.movable:
            self.move_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.move_button.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )

    @QtCore.pyqtSlot(bool)
    def toggle_power(self, powered):
        self.powered = not powered
        if powered:
            self.power_button.setText("ON")
        else:
            self.power_button.setText("OFF")


def connect_button_to_axis(
        widget,
        button,
        actions,
        axis,
        property
):
    def connection():
        try:
            widget.value = float(widget.input.text())
        except ValueError:
            widget.value = 0
        setattr(axis, property, widget.value)

    for action in actions:
        event = getattr(button, action)
        event.connect(connection)

    return connection


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SetWidget(title="HALLO", unit="m", symbols=7)
    window.show()
    sys.exit(app.exec())
