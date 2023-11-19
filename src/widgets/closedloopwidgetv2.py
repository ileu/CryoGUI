import sys

from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QGridLayout,
)

from src.controller import AMC300Controller
from src.dummies.dummycontroller import DummyAMC300Controller
from src.widgets.utilitywidgets import SetWidget, ControlBar, IncrementWidget


class ClosedLoopWidget(QWidget):
    def __init__(
        self,
        parent: QWidget = None,
        controller: AMC300Controller = None,
        axis_index: int = 0,
        title: str = "Quantity",
        symbols: int = 7,
        unit: str = "",
        **kwargs,
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

        self.position_widget = SetWidget(
            title="Position", symbols=8, unit="um", top=15e3
        )
        self.step_widget = IncrementWidget(title="Step")

        self.init_ui()

        self.controller_thread = QThread()
        self.controller = controller
        self.controller.moveToThread(self.controller_thread)

        self.controller.axes[axis_index].statusUpdated.connect(
            self.control_bar.status_label.setText
        )

        self.controller.axes[axis_index].positionUpdated.connect(self.set_position)
        self.controller.axes[axis_index].valuesUpdated.connect(self.set_values)
        self.controller.axes[axis_index].targetPositionUpdated.connect(
            self.set_target_position
        )

        self.control_bar.active_button.clicked.connect(
            self.controller.axes[axis_index].set_axis_control_move
        )
        self.controller.axes[axis_index].activivityUpdated.connect(
            self.control_bar.active_button.setChecked
        )
        self.control_bar.mode_button.clicked.connect(
            self.controller.axes[axis_index].set_status_axis
        )
        self.controller.axes[axis_index].modeUpdated.connect(
            self.control_bar.mode_button.setChecked
        )

        self.controller.axes[axis_index].update_values()
        self.controller.axes[axis_index].update_position()
        self.controller.axes[axis_index].get_target_position()
        self.controller.axes[axis_index].get_status_axis()
        self.controller.axes[axis_index].get_axis_movement()

        self.voltage_widget.valueChanged.connect(
            lambda value: self.controller.axes[axis_index].set_value(value, "voltage")
        )
        self.frequency_widget.valueChanged.connect(
            lambda value: self.controller.axes[axis_index].set_value(value, "frequency")
        )
        self.offset_widget.valueChanged.connect(
            lambda value: self.controller.axes[axis_index].set_value(value, "offset")
        )
        self.position_widget.valueChanged.connect(
            self.controller.axes[axis_index].set_target_position
        )

        print("Connecting axis")
        self.update_timer = QTimer()
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(
            self.controller.axes[axis_index].update_position
        )
        self.update_timer.start()
        print("Connected axis")
        self.controller_thread.start()

    def init_ui(self):
        self.position_display.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        self.position_display.setStyleSheet(
            "QLabel { background-color: white; border: 2px solid black; border-radius: 5px; font-size: 32px;}"
            "QLabel:disabled { background-color: rgb(200,200,200); }"
        )
        # self.position_display.setFixedSize((self.symbols + len(self.unit)) * 20, 50)

        layout = QGridLayout()
        layout.addWidget(self.control_bar, 0, 0, 1, 3)

        layout.addWidget(self.position_display, 1, 0)
        layout.addWidget(
            self.position_widget,
            1,
            1,
            alignment=Qt.AlignTop,
        )
        layout.addWidget(self.step_widget, 1, 2)

        layout.addWidget(self.voltage_widget, 2, 0)
        layout.addWidget(self.frequency_widget, 2, 1)
        layout.addWidget(self.offset_widget, 2, 2)

        layout.setColumnStretch(3, 1)
        layout.setRowStretch(3, 1)
        self.setLayout(layout)

    def set_position(self, value):
        self.position_display.setText(f"{value:.{2}f}" + self.unit)

    def set_values(self, values):
        self.voltage_widget.set_input_text(values[0])
        self.frequency_widget.set_input_text(values[1])
        self.offset_widget.set_input_text(values[2])

    def set_target_position(self, value):
        self.position_widget.set_input_text(f"{value:.{2}f}")

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
    controller = DummyAMC300Controller(IP)
    controller.connect()

    app = QApplication(sys.argv)
    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    for axis in range(3):
        clw2 = ClosedLoopWidget(controller=controller, axis_index=axis, unit="um")
        layout.addWidget(clw2)
    window.show()
    sys.exit(app.exec())
