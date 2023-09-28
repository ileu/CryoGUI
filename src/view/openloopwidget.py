from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QStyle,
    QGridLayout, QFrame
)
from pymeasure.instruments.attocube.anc300 import Axis

from src.view.utilitywidgets import SetWidget, IncrementWidget, push_button_style, ControlBar


class DummyAxis:
    def __getattr__(self, item):
        print(f"get {item}")
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        print(f"set {key}: {value}")
        super().__setattr__(key, value)


class OpenLoopWidget(QFrame):
    def __init__(
            self,
            parent: QWidget = None,
            axis: Axis | DummyAxis = None,
            title: str = "Quantity",
            **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.control_bar = ControlBar()

        self.control_bar.title_label.setText(title)
        self.control_bar.status_label.setText("Status: Disconnected")

        self.voltage_widget = SetWidget(title="Voltage", symbols=8, unit="V")
        self.frequency_widget = SetWidget(title="Frequency", symbols=8, unit="Hz")
        self.offset_widget = SetWidget(title="Offset", symbols=8, unit="V")

        self.step_widget = IncrementWidget(title="Step")

        self.optimize_button = QPushButton("Optimize")
        self.cmover_button = QPushButton(">>")
        self.cmovel_button = QPushButton("<<")

        self.grounded = False
        self.movable = False

        self.initUI()

        if axis is None:
            self.axis: Axis = None
            self.deactivate()
        else:
            self.axis = axis

    def initUI(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.optimize_button.setStyleSheet(push_button_style)
        self.optimize_button.setFixedSize(100, 30)

        self.cmover_button.setStyleSheet(push_button_style)
        self.cmover_button.setFixedSize(40, 20)

        self.cmovel_button.setStyleSheet(push_button_style)
        self.cmovel_button.setFixedSize(40, 20)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)

        main_layout.addWidget(self.control_bar)
        control_layout = QGridLayout()
        control_layout.setSpacing(1)
        main_layout.addLayout(
            control_layout
        )

        control_layout.addWidget(
            self.voltage_widget, 0, 0
        )
        control_layout.addWidget(
            self.frequency_widget, 1, 0
        )
        control_layout.addWidget(
            self.offset_widget, 0, 1
        )
        control_layout.addWidget(
            self.optimize_button, 1, 1, alignment=Qt.AlignmentFlag.AlignCenter
        )

        step_layout = QVBoxLayout()
        step_layout.setSpacing(0)
        step_layout.addWidget(self.step_widget)

        cmove_layout = QHBoxLayout()
        cmove_layout.setSpacing(0)
        cmove_layout.addWidget(self.cmovel_button, alignment=Qt.AlignmentFlag.AlignRight)
        cmove_layout.addWidget(self.cmover_button, alignment=Qt.AlignmentFlag.AlignLeft)

        step_layout.addLayout(cmove_layout)
        control_layout.addLayout(step_layout, 0, 2, 2, 1)

        main_layout.addStretch()

        self.setLayout(main_layout)

    def refresh_values(self):
        pass

    def setVoltage(self):
        try:
            self.voltage_widget.value = float(self.voltage_widget.input.text())
        except ValueError:
            self.voltage_widget.value = 0
        self.axis.voltage = self.voltage_widget.value

    def setFrequency(self):
        try:
            self.frequency_widget.value = float(self.frequency_widget.input.text())
        except ValueError:
            self.frequency_widget.value = 100
        self.axis.frequency = self.frequency_widget.value

    def setOffsetVoltage(self):
        try:
            self.offset_widget.value = float(self.offset_widget.input.text())
        except ValueError:
            self.offset_widget.value = 0
        self.axis.offset_voltage = self.offset_widget.value

    def stepp(self):
        try:
            self.step_widget.value = float(self.step_widget.input.text())
        except ValueError:
            self.step_widget.value = 0
        self.axis.step = self.step_widget.value

    def connect_to_axis(self, widget, property):
        def connection():
            try:
                widget.value = float(widget.input.text())
            except ValueError:
                widget.value = 0
            setattr(self.axis, property, widget.value)
        return connection

    def activate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

        self.voltage_widget.set_button.clicked.connect(self.connect_to_axis(self.voltage_widget, "voltage"))
        self.frequency_widget.set_button.clicked.connect(self.setFrequency)
        self.offset_widget.set_button.clicked.connect(self.setOffsetVoltage)
        self.step_widget.minus_button.clicked.connect(self.stepp)
        self.step_widget.plus_button.clicked.connect(self.stepp)
        self.cmover_button.pressed.connect(self.stepp)
        self.cmovel_button.released.connect(self.stepp)

    def deactivate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(False)


if __name__ == "__main__":
    app = QApplication([])
    olw = OpenLoopWidget(axis=DummyAxis())
    olw.activate()
    olw.show()
    app.exec()
