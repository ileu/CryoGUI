import sys

from PyQt6.QtGui import QDoubleValidator
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt6.QtCore import Qt

from src.controller._quantities import PositionQty


class NumberWidget(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        title: str = "Quantity",
        symbols: int = 7,
        unit: str = "",
        positionqty: PositionQty = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.value = 0.0

        self.title_label = QLabel(title)
        self.status_label = QLabel("Status: Disconnected")
        self.number_display = QLabel(str(self.value) + unit)

        self.number_input = QLineEdit()
        self.incrm_input = QLineEdit()
        self.plus_button = QPushButton("+")
        self.minus_button = QPushButton("-")
        self.set_button = QPushButton("Set")

        self.gnd_button = QPushButton("GND")

        self.positionqty = positionqty

        self.symbols = symbols
        self.unit = unit
        self.grounded = False

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Number Widget")

        self.number_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.number_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 16px;}"
            "QLineEdit:disabled { background-color: rgb(200,200,200); }"
        )
        self.number_input.setFixedSize((self.symbols + len(self.unit)) * 20, 24)
        self.number_input.setValidator(QDoubleValidator())
        self.number_input.returnPressed.connect(self.setValue)
        self.number_input.setPlaceholderText(self.unit)

        self.incrm_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.incrm_input.setStyleSheet(
            "QLineEdit { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLineEdit:disabled { background-color: rgb(200,200,200); }"
        )
        self.incrm_input.setFixedSize(65, 50)
        self.incrm_input.setValidator(QDoubleValidator())
        self.incrm_input.returnPressed.connect(self.incrementValue)
        self.incrm_input.setPlaceholderText("0")

        self.number_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.number_display.setStyleSheet(
            "QLabel { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLabel:disabled { background-color: rgb(200,200,200); }"
        )
        self.number_display.setFixedSize((self.symbols + len(self.unit)) * 20, 50)

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

        self.set_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 20px;}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.set_button.setFixedSize(60, 24)
        self.set_button.clicked.connect(self.setValue)

        self.gnd_button.setCheckable(True)
        self.gnd_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 16px; font-weight: bold;"
            "background-color: rgb(180,180,255);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.gnd_button.setFixedSize(40, 20)

        main_layout = QVBoxLayout()
        text_layout = QHBoxLayout()
        text_layout.addWidget(self.title_label)
        text_layout.addStretch()
        text_layout.addWidget(self.status_label)
        text_layout.addWidget(self.gnd_button)

        main_layout.addLayout(text_layout)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        control_layout.addWidget(self.number_display)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(0)
        button_layout.addStretch()

        button_layout.addWidget(self.set_button)
        button_layout.addStretch()

        input_layout = QVBoxLayout()
        input_layout.setSpacing(2)

        input_layout.addWidget(self.number_input)
        input_layout.addLayout(button_layout)
        control_layout.addLayout(input_layout)

        increment_layout = QHBoxLayout()
        increment_layout.setSpacing(2)
        increment_layout.addWidget(self.plus_button)
        increment_layout.addWidget(self.incrm_input)
        increment_layout.addWidget(self.minus_button)

        control_layout.addLayout(increment_layout)

        main_layout.addLayout(control_layout)

        self.setLayout(main_layout)

    def _check_grounded(self):
        if not self.gnd_button.isChecked():
            self.status_label.setText("Status: Axis is grounded")
            return True
        return False

    def incrementValue(self):
        if self._check_grounded():
            return

        try:
            incr_number = float(self.incrm_input.text())
        except ValueError:
            incr_number = 0.0

        try:
            inp_number = float(self.number_input.text())
        except ValueError:
            inp_number = 0.0

        self.number_input.setText(str(inp_number + incr_number))
        self.positionqty.position_um = inp_number + incr_number

    def decrementValue(self):
        if self._check_grounded():
            return

        try:
            incr_number = float(self.incrm_input.text())
        except ValueError:
            incr_number = 0.0

        try:
            inp_number = float(self.number_input.text())
        except ValueError:
            inp_number = 0.0

        self.number_input.setText(str(inp_number - incr_number))
        self.positionqty.position_um = inp_number - incr_number

    def updateNumberDisplay(self):
        try:
            self.value = self.positionqty.position_um
            self.number_display.setText("{:.7}".format(self.value) + self.unit)
        except AttributeError:
            self.status_label.setText("Error: Axis is not a position quantity")
            return
        except Exception as e:
            print(e)
            self.status_label.setText("Error")
            return

    def setValue(self):
        if self._check_grounded():
            return

        try:
            new_number = float(self.number_input.text())
        except ValueError:
            self.status_label.setText("Status: Invalid value")
            return
        try:
            self.positionqty.position_um = new_number
        except AttributeError:
            self.status_label.setText("Error: Axis is not a position quantity")
            return
        except Exception as e:
            print(e)
            self.status_label.setText("Error")
            return

    def setStatus(self, status: str):
        self.status_label.setText("Status: " + status)

    def activate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

        self.value = self.positionqty.position_um
        self.number_input.setText(str(self.value))

    def deactivate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NumberWidget()
    window.show()
    sys.exit(app.exec())
