import datetime
import os
import random
import sys
import time

from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QWidget,
    QFileDialog,
    QGridLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QLineEdit,
    QHBoxLayout,
    QSpacerItem,
    QVBoxLayout,
)

from pyqtgraph import PlotWidget
import pyqtgraph as pg

from src.controller.attodry800 import AttoDry800Controller

# from src.AttoDRY import AttoDRY, Cryostats

from src.dummies.dummycontroller import DummyAttoDRY


class CryoWidget(QWidget):
    updatedData = pyqtSignal(list)
    updatedUserTemperature = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.serial_port = None
        self.log_file_location = None

        # self.attodry_controller = AttoDRY(
        #     setup_version=Cryostats.ATTODRY800, com_port=None
        # )
        self.controller = AttoDry800Controller()
        self.attodry_controller = DummyAttoDRY()
        self.is_connected = False
        self.action_monitor = QTextEdit()
        self.port_combo = QComboBox()
        self.connect_button = QPushButton("Connect")

        self.stage_temp_canvas = PlotWidget(title="Sample Temperature")
        self.stage_pressure_canvas = PlotWidget(title="Sample Space Pressure")
        self.cold_temp_canvas = PlotWidget(title="Cold Plate Temperature")
        self.heater_power_canvas = PlotWidget(title="Heater Power")
        self.turbo_pump_canvas = PlotWidget(title="Turbo Pump Frequency")

        self.logging_timer = QTimer()
        self.logging_timer.timeout.connect(self.get_values)

        self.canvases: list[PlotWidget] = [
            self.stage_temp_canvas,
            self.stage_pressure_canvas,
            self.cold_temp_canvas,
            self.heater_power_canvas,
            self.turbo_pump_canvas,
        ]

        self.data_names = [
            "Temperature",
            "Pressure",
            "Temperature",
            "Power",
            "Frequency",
        ]
        self.data_units = ["K", "mbar", "K", "W", "Hz"]
        self.data_titles = [
            "sample-temp_K",
            "sample-pres_mbar",
            "cold-plate-temp_K",
            "heater-power_W",
            "turbo-pump-freq_Hz",
        ]

        self.data = [[] for i in range(5)]
        self.user_temperature = 4

        self.main_layout = QHBoxLayout()

        self.init_ui()

        for widget in self.findChildren((QPushButton, QLineEdit)):
            if widget == self.connect_button or widget == self.port_combo:
                continue
            widget.setEnabled(False)

        self.controller.updatedValues.connect(self.plot_data)
        self.controller.updatedValues.connect(self.log_data)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.read_and_log_data)
        # self.log_file = None

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        setup_layout = QGridLayout()
        ports = [port for port in QSerialPortInfo.availablePorts()]

        self.port_combo.addItems([port.portName() for port in ports])

        self.logging_interval_edit = QLineEdit("1000")
        self.logging_interval_edit.setToolTip("Needs to be bigger than 100ms")
        self.logging_interval_edit.editingFinished.connect(
            lambda: self.logging_timer.setInterval(
                int(self.logging_interval_edit.text())
            )
        )
        self.logging_interval_edit.inputRejected.connect(
            lambda: print("rejected", self.logging_interval_edit.hasAcceptableInput())
        )
        # self.logging_interval_edit.sele
        self.logging_interval_edit.setValidator(QIntValidator(bottom=500))
        self.logging_interval_edit.editingFinished.connect(
            lambda: self.logging_interval_edit.setStyleSheet(
                "background-color: red"
                if int(self.logging_interval_edit.text()) < 100
                else "background-color: white"
            )
        )
        self.logging_interval_edit.setEnabled(False)

        self.connect_button.clicked.connect(self.connect_controller)

        self.log_file_browse = QPushButton("Start Logging")
        self.log_file_browse.clicked.connect(self.logging_manager)
        self.log_file_browse.setCheckable(True)

        self.file_locator = QLineEdit()

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_controller)

        setup_layout.addWidget(QLabel("Serial Port"), 0, 0)
        setup_layout.addWidget(self.port_combo, 0, 1)
        setup_layout.addWidget(self.connect_button, 0, 3)
        setup_layout.addWidget(self.disconnect_button, 0, 4)

        setup_layout.addWidget(self.file_locator, 1, 0, 1, 4)
        setup_layout.addWidget(self.log_file_browse, 1, 4)

        setup_layout.addWidget(QLabel("Logging Interval (ms)"), 2, 2)
        setup_layout.addWidget(
            self.logging_interval_edit,
            2,
            3,
            1,
            1,
        )

        # main_layout.addLayout(setup_layout)
        self.action_monitor.setReadOnly(True)

        controller_layout = QGridLayout()
        self.base_temperature_button = QPushButton("Base Temperature")
        self.base_temperature_button.clicked.connect(
            self.attodry_controller.goToBaseTemperature
        )
        controller_layout.addWidget(self.base_temperature_button, 0, 0)

        self.heat_up_button = QPushButton("Heat Up")
        # self.heat_up_button.clicked.connect(self.attodry_controller.startSampleExchange)
        controller_layout.addWidget(self.heat_up_button, 1, 0)

        self.temperature_control_button = QPushButton("Activate Temperature control")
        controller_layout.addWidget(self.temperature_control_button, 2, 0)

        self.user_temperature_edit = QLineEdit()
        self.user_temperature_edit.setText(str(self.user_temperature))
        controller_layout.addWidget(self.user_temperature_edit, 2, 1)

        self.set_pid_button = QPushButton("Set PID")
        controller_layout.addWidget(self.set_pid_button, 2, 2)

        self.p_edit = QLineEdit()
        controller_layout.addWidget(self.p_edit, 2, 3)

        self.i_edit = QLineEdit()
        controller_layout.addWidget(self.i_edit, 2, 4)

        self.d_edit = QLineEdit()
        # controller_layout.addWidget(self.d_edit, 2, 5)

        self.break_valve_button = QPushButton("Break Sample Valve")
        # self.break_valve_button.clicked.connect(
        #     self.attodry_controller.toggleBreakVac800Valve
        # )
        # controller_layout.addWidget(self.break_valve_button, 0, 6)

        self.confirm_button = QPushButton("Confirm")
        # self.confirm_button.clicked.connect(self.attodry_controller.Confirm)
        controller_layout.addWidget(self.confirm_button, 0, 3)

        self.cancel_button = QPushButton("Cancel")
        # self.cancel_button.clicked.connect(self.attodry_controller.Cancel)
        controller_layout.addWidget(self.cancel_button, 0, 4)

        plot_layout = QGridLayout()

        plot_layout.addWidget(self.stage_temp_canvas, 0, 0)
        plot_layout.addWidget(self.stage_pressure_canvas, 1, 0)
        plot_layout.addWidget(self.turbo_pump_canvas, 2, 0)

        plot_layout.addWidget(self.cold_temp_canvas, 0, 1)
        plot_layout.addWidget(self.heater_power_canvas, 1, 1)
        plot_layout.addWidget(self.action_monitor, 2, 1)

        control_layout = QHBoxLayout()

        control_layout.addLayout(setup_layout)
        # control_layout.addStretch()
        control_layout.addLayout(controller_layout)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(plot_layout)

        for i, plot_widget in enumerate(self.canvases):
            plot_widget.showGrid(x=True, y=True, alpha=0.5)
            # plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(
                self.data_names[i], units=self.data_units[i]
            )
            plot_widget.getAxis("bottom").setPen(pg.mkPen(color="k"))
            plot_widget.getAxis("left").setPen(pg.mkPen(color="k"))
            plot_widget.showAxis("right")
            plot_widget.getAxis("right").setStyle(showValues=False)
            plot_widget.getAxis("right").setPen(pg.mkPen(color="k"))
            plot_widget.showAxis("top")
            plot_widget.getAxis("top").setStyle(showValues=False)
            plot_widget.getAxis("top").setPen(pg.mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.getPlotItem().setContentsMargins(0, 0, 25, 10)
            plot_widget.setStyleSheet(
                "border: 2px solid gray; border-radius: 5px; padding: 2px; background-color: white"
            )
            if i != 0:
                plot_widget.setXLink(self.canvases[0])

    def logging_manager(self, running: bool = False):
        if running:
            dialog = QFileDialog(self)
            dialog.setDirectory(os.path.join(os.path.dirname(__file__)))
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setViewMode(QFileDialog.ViewMode.List)

            date = datetime.datetime.now().strftime("%Y%m%d")

            filename, filetype = dialog.getSaveFileName(
                self,
                "Save File",
                f"{date}_log_file",
                "Text Files (*.txt);; CSV (*.csv)",
            )
            self.action_monitor.append(f"Got log file path: {filename}")
            if filename:
                self.file_locator.setText(filename)
                if not os.path.exists(filename):
                    with open(
                        filename,
                        "a",
                    ) as f:
                        f.write("time," + ",".join(self.data_titles) + "\n")
                        f.flush()
                self.log_file_browse.setText("Stop Logging")
                self.log_file_location = filename
                self.logging_timer.start(1000)
                self.file_locator.setEnabled(False)
                self.logging_interval_edit.setEnabled(True)
                self.action_monitor.append(f"Started logging to {filename}")
            else:
                self.log_file_browse.setChecked(False)
        else:
            self.log_file_browse.setText("Start Logging")
            self.logging_timer.stop()

            self.action_monitor.append(f"Logging stopped")
            # self.log_file.close()
            # self.log_file = None

    def connect_controller(self):
        serial_port = str(self.port_combo.currentText())
        self.action_monitor.append(f"Connecting to serial port {serial_port}")
        print(serial_port)
        print(self.port_combo.currentIndex())
        print(self.port_combo.currentData())
        try:
            self.attodry_controller.begin()
            self.attodry_controller.Connect(serial_port)
            # time.sleep(30)

            for widget in self.findChildren(QWidget):
                widget.setEnabled(True)
            self.connect_button.setEnabled(False)
            self.action_monitor.append(f"Connected to serial port {serial_port}")
            self.is_connected = True
        except Exception as e:
            self.action_monitor.append(f"Failed to connect to serial port: {str(e)}")

    def disconnect_controller(self):
        try:
            self.attodry_controller.Disconnect()
            self.attodry_controller.end()
            for widget in self.findChildren((QPushButton, QLineEdit)):
                if widget == self.connect_button or widget == self.port_combo:
                    continue
                widget.setEnabled(False)
            self.connect_button.setEnabled(True)
            self.action_monitor.append(f"Disconnected from serial port")
            # self.timer.stop()
        except Exception as e:
            self.action_monitor.append(
                f"Failed to disconnect from serial port: {str(e)}"
            )

    def get_values(self):
        for i in range(4):
            try:
                temperature = self.attodry_controller.getSampleTemperature()
                pressure = self.attodry_controller.getPressure800()
                lk_sample_temperature = self.attodry_controller.get4KStageTemperature()
                heat_power = self.attodry_controller.getSampleHeaterPower()
                turbo_pump_frequency = self.attodry_controller.GetTurbopumpFrequ800()

                user_temperature = self.attodry_controller.getUserTemperature()

                self.updatedUserTemperature.emit(user_temperature)

                data = [
                    temperature,
                    pressure,
                    lk_sample_temperature,
                    heat_power,
                    turbo_pump_frequency,
                ]

                self.user_temperature = user_temperature

                # data = [
                #     1 + random.random(),
                #     2 + random.random(),
                #     3 + random.random(),
                #     4 + random.random(),
                #     5 + random.random(),
                # ]

                self.updatedData.emit(data)
                break
            except Exception as e:
                self.action_monitor.append(f"Failed to get values {e}")
                self.action_monitor.append(f"Retrying {4-i} times in 1 second")
                time.sleep(1)

    def plot_data(self, new_data_points):
        for data, data_point, plot_widget in zip(
            self.data, new_data_points, self.canvases
        ):
            print(data_point)
            data.append(data_point)
            if len(data) > 200:
                data = data[-200:]
            plot_widget.plot(data, clear=True, pen=pg.mkPen("b"))  # Blue pen
            if len(data) > 1:
                plot_widget.enableAutoRange("x")

    def log_data(self, new_data_points):
        with open(
            self.log_file_location,
            "a",
        ) as f:
            line = str(time.time())
            line += ",".join(map(str, new_data_points))
            f.write(line + "\n")
            f.flush()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryoWidget()
    window.setWindowTitle("Logger Interface")
    window.setGeometry(100, 20, 1500, 800)
    window.show()
    sys.exit(app.exec())
