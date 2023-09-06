import sys
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, QLabel


class IncrementWidget(QWidget):
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

        self.input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid black; font-size: 32px;}"
            "QLineEdit:disabled { background-color: rgb(200,200,200); }"
        )
        self.input.setFixedSize(65, 50)
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
        self.plus_button.setFixedSize(24, 50)
        self.plus_button.clicked.connect(self.incrementValue)

        self.minus_button.setStyleSheet(
            "QPushButton { border: 2px solid black; "
            "border-top-right-radius: 5px;  border-bottom-right-radius: 5px; "
            "font-size: 32px; text-align: center; padding-bottom: 5px}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.minus_button.setFixedSize(24, 50)
        self.minus_button.clicked.connect(self.decrementValue)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(2)

        main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)

        side_layout = QHBoxLayout()
        side_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        side_layout.setSpacing(0)

        side_layout.addWidget(self.plus_button, alignment=Qt.AlignmentFlag.AlignRight)
        side_layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignCenter)
        side_layout.addWidget(self.minus_button, alignment=Qt.AlignmentFlag.AlignLeft)

        main_layout.addLayout(side_layout)

        self.setLayout(main_layout)

    def incrementValue(self):
        try:
            incr_number = float(self.input.text())
        except ValueError:
            return

        self.value += incr_number
        if self._callOnValueChanged is not None:
            self._callOnValueChanged(value=self.value)

    def decrementValue(self):
        try:
            incr_number = float(self.input.text())
        except ValueError:
            return

        self.value -= incr_number
        if self._callOnValueChanged is not None:
            self._callOnValueChanged(value=self.value)

    def onValueChanged(self, callback: Callable[[float], None]) -> None:
        self._callOnValueChanged = callback


class SetWidget(QWidget):

    def __init__(self, title="", symbols: int = 7, unit: str = "", **kwargs):
        super().__init__()
        self.value = 0.0
        self.symbols = symbols
        self.unit = unit

        self.title = QLabel(title + unit)
        self.input = QLineEdit()
        self.set_button = QPushButton("Set")

        self._callOnValueChanged = None

        self.initUI()

    def initUI(self):
        self.input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 16px;}"
            "QLineEdit:disabled { background-color: rgb(200,200,200); }"
        )
        self.input.setFixedSize((self.symbols + len(self.unit)) * 20, 24)
        self.input.setValidator(QDoubleValidator())
        self.input.returnPressed.connect(self.setValue)
        self.input.setPlaceholderText(self.unit)

        self.set_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 20px;}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.set_button.setFixedSize(60, 24)
        self.set_button.clicked.connect(self.setValue)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(2)

        main_layout.addWidget(self.title, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.input, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.set_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.setLayout(main_layout)

    def setValue(self):
        try:
            self.value = float(self.input.text())
        except ValueError:
            self.value = 0.0

        if self._callOnValueChanged is not None:
            self._callOnValueChanged(value=self.value)

    def onValueChanged(self, callback: Callable[[float], None]) -> None:
        self._callOnValueChanged = callback


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IncrementWidget()
    window.show()
    sys.exit(app.exec())
