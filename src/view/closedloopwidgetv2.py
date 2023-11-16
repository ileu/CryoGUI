import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout

from src.controller import AMC300Controller
from src.view.utilitywidgets import SetWidget, ControlBar, IncrementWidget


class ClosedLoopWidgetv2(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        controller: AMC300Controller = None,
        axis_index: int = 0,
        title: str = "Quantity",
        symbols: int = 7,
        unit: str = "",
        **kwargs
    ):
        super().__init__(parent=parent, **kwargs)

        self.title = title
        self.value = 0.0
        self.symbols = symbols
        self.unit = unit

        self.control_bar = ControlBar(off_mode="GND")
        self.control_bar.title_label.setText(title)

        self.position_display = QLabel(str(self.value) + unit)

        self.voltage_widget = SetWidget(title="Voltage", symbols=8, unit="V", top=60)
        self.frequency_widget = SetWidget(
            title="Frequency", symbols=8, unit="Hz", top=900
        )
        self.offset_widget = SetWidget(title="Offset", symbols=8, unit="V", top=90)

        self.position_widget = SetWidget(title="Position", symbols=8, unit="um", top=90)
        self.step_widget = IncrementWidget(title="Step")

        self.init_ui()

        self.controller = controller

        self.controller.axes[axis_index].statusUpdated.connect(
            self.control_bar.status_label.setText
        )

        self.controller.axes[axis_index].positionUpdated.connect(self.set_position)
        self.controller.axes[axis_index].valuesUpdated.connect(self.set_values)

        self.control_bar.active_button.clicked.connect(
            self.controller.axes[axis_index].set_axis_control_move
        )
        self.control_bar.mode_button.clicked.connect(
            self.controller.axes[axis_index].set_status_axis
        )

    def init_ui(self):
        self.position_display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.position_display.setStyleSheet(
            "QLabel { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLabel:disabled { background-color: rgb(200,200,200); }"
        )
        # self.position_display.setFixedSize((self.symbols + len(self.unit)) * 20, 50)

        layout = QVBoxLayout()
        layout.addWidget(self.control_bar)

        position_layout = QHBoxLayout()

        position_layout.addWidget(self.position_display, stretch=1)
        position_layout.addWidget(
            self.position_widget,
            stretch=1,
            alignment=Qt.AlignTop,
        )
        position_layout.addWidget(self.step_widget, stretch=1)

        control_layout = QHBoxLayout()
        control_layout.addWidget(self.voltage_widget, stretch=1)
        control_layout.addWidget(self.frequency_widget, stretch=1)
        control_layout.addWidget(self.offset_widget, stretch=1)

        layout.addLayout(position_layout)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def set_position(self, value):
        self.position_display.setText(str(value) + self.unit)

    def set_values(self, values):
        self.voltage_widget.set_input_text(values[0])
        self.frequency_widget.set_input_text(values[1])
        self.offset_widget.set_input_text(values[2])

    def connect_axis(self, axis):
        self.controller.axis = axis

    def activate(self):
        self.control_bar.activate()
        self.voltage_widget.activate()
        self.frequency_widget.activate()
        self.offset_widget.activate()
        self.position_widget.activate()
        self.step_widget.activate()
        self.position_display.setEnabled(True)

    def deactivate(self):
        self.control_bar.deactivate()
        self.voltage_widget.deactivate()
        self.frequency_widget.deactivate()
        self.offset_widget.deactivate()
        self.position_widget.deactivate()
        self.step_widget.deactivate()
        self.position_display.setEnabled(False)


if __name__ == "__main__":
    IP = "192.168.1.1"
    axis = 0
    controller = AMC300Controller(IP)
    controller.connect()

    app = QApplication(sys.argv)
    window = ClosedLoopWidgetv2(controller=controller, axis_index=axis)
    window.show()
    sys.exit(app.exec())
