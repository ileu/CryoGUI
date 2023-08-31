import sys

from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from src.controller._quantities import PositionQty


class NumberWidget(QWidget):
    def __init__(self, parent: QWidget = None, title: str = "Quantity", symbols: int = 7, unit: str = "",
                 positionqty: PositionQty = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.value = 0.0

        self.title_label = QLabel(title)
        self.status_label = QLabel("Status: Disconnected")
        self.number_display = QLabel(str(self.value) + unit)

        self.number_input = QLineEdit()
        self.plus_button = QPushButton('+')
        self.minus_button = QPushButton('-')
        self.set_button = QPushButton('Set')

        self.positionqty = positionqty

        self.symbols = symbols
        self.unit = unit

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Number Widget')

        self.number_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.number_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLineEdit:disabled { background-color: rgb(200,200,200); }"
        )
        self.number_input.setFixedSize((self.symbols + len(self.unit)) * 20, 50)
        self.number_input.setValidator(QDoubleValidator())
        self.number_input.returnPressed.connect(self.setValue)
        self.number_input.setPlaceholderText(self.unit)

        self.number_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.number_display.setStyleSheet(
            "QLabel { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLabel:disabled { background-color: rgb(200,200,200); }"
        )
        self.number_display.setFixedSize((self.symbols + len(self.unit)) * 20, 50)

        self.plus_button.setStyleSheet("QPushButton { border: 2px solid black; "
                                       "border-top-left-radius: 5px;  border-bottom-left-radius: 5px; "
                                       "font-size: 20px; text-align: center; padding-bottom: 5px } "
                                       "QPushButton:hover {background-color: rgb(228,241,251); }"
                                       "QPushButton:pressed {background-color: rgb(204,228,247); }"
                                       "QPushButton:disabled {background-color: rgb(200,200,200); }")
        self.plus_button.setFixedSize(24, 24)
        self.plus_button.clicked.connect(self.incrementNumber)

        self.minus_button.setStyleSheet("QPushButton { border: 2px solid black; "
                                        "font-size: 20px; text-align: center; padding-bottom: 5px}"
                                        "QPushButton:hover {background-color: rgb(228,241,251); }"
                                        "QPushButton:pressed {background-color: rgb(204,228,247); }"
                                        "QPushButton:disabled {background-color: rgb(200,200,200); }")
        self.minus_button.setFixedSize(24, 24)
        self.minus_button.clicked.connect(self.decrementNumber)

        self.set_button.setStyleSheet("QPushButton {border: 2px solid black; padding-bottom: 2px; "
                                      "border-top-right-radius: 5px; border-bottom-right-radius: 5px; font-size: 20px;}"
                                      "QPushButton:hover {background-color: rgb(228,241,251); }"
                                      "QPushButton:pressed {background-color: rgb(204,228,247); }"
                                      "QPushButton:disabled {background-color: rgb(200,200,200); }")
        self.set_button.setFixedSize(40, 24)
        self.set_button.clicked.connect(self.setValue)

        layout = QVBoxLayout()
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.title_label)
        text_layout.addStretch()
        text_layout.addWidget(self.status_label)
        layout.addLayout(text_layout)

        number_input_layout = QHBoxLayout()
        number_input_layout.setSpacing(5)
        number_input_layout.addWidget(self.number_display)
        number_input_layout.addWidget(self.number_input)
        layout.addLayout(number_input_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        button_layout.addWidget(self.plus_button)
        button_layout.addWidget(self.minus_button)
        button_layout.addWidget(self.set_button)
        number_input_layout.addLayout(button_layout)

        self.setLayout(layout)

    def incrementNumber(self):
        try:
            new_number = float(self.number_input.text())
        except ValueError:
            new_number = 0.0
        new_number += 1.0
        self.number_input.setText(str(new_number))

    def decrementNumber(self):
        try:
            new_number = float(self.number_input.text())
        except ValueError:
            new_number = 0.0
        new_number -= 1.0
        self.number_input.setText(str(new_number))

    def updateNumberDisplay(self):
        self.value = self.positionqty.position_um
        self.number_display.setText("{:.7}".format(self.value) + self.unit)

    def setValue(self):
        try:
            new_number = float(self.number_input.text())
        except ValueError:
            self.status_label.setText("Status: Invalid value")
            return
        try:
            self.positionqty.position_um = new_number
        except Exception as e:
            print(e)
            self.status_label.setText("Error: " + e)
            return

    def setStatus(self, status: str):
        self.status_label.setText("Status: " + status)

    def activate(self):
        self.number_display.setEnabled(True)
        self.number_input.setEnabled(True)
        self.plus_button.setEnabled(True)
        self.minus_button.setEnabled(True)
        self.set_button.setEnabled(True)

    def deactivate(self):
        self.number_display.setEnabled(False)
        self.number_input.setEnabled(False)
        self.plus_button.setEnabled(False)
        self.minus_button.setEnabled(False)
        self.set_button.setEnabled(False)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NumberWidget()
    window.show()
    sys.exit(app.exec())
