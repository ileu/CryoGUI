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
)

from pyqtgraph import PlotWidget
import pyqtgraph as pg

# from src.AttoDRY import AttoDRY, Cryostats

from src.dummies.dummycontroller import DummyAttoDRY


class Messenger(QThread):
    finished = pyqtSignal()
    failed = pyqtSignal()

    def __init__(self, device, message):
        super().__init__()
        self.device = device
        self.message = message

    def run(self):
        pass
        # try:
        # self.device


class CryoWidget(QMainWindow):
    updatedData = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.serial_port = None
        self.log_file_location = None

        # self.attodry_controller = AttoDRY(
        #     setup_version=Cryostats.ATTODRY800, com_port=None
        # )

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

        self.user_temperature = 4

        self.canvases = [
            self.stage_temp_canvas,
            self.stage_pressure_canvas,
            self.cold_temp_canvas,
            self.heater_power_canvas,
            self.turbo_pump_canvas,
        ]

        self.data_names = [
            "Temperature / K",
            "Pressure / mbar",
            "Temperature / K",
            "Power / W",
            "Frequency / Hz",
        ]
        self.data_titles = [
            "sample-temp_K",
            "sample-pres_mbar",
            "cold-plate-temp_K",
            "heater-power_W",
            "turbo-pump-freq_Hz",
        ]

        self.data = [[] for i in range(5)]

        self.init_ui()

        for widget in self.findChildren((QPushButton, QLineEdit)):
            if widget == self.connect_button or widget == self.port_combo:
                continue
            widget.setEnabled(False)

        self.updatedData.connect(self.plot_data)
        self.updatedData.connect(self.log_data)

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.read_and_log_data)
        # self.log_file = None

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)

        self.central_widget.setLayout(self.layout)

        port_label = QLabel("Port")
        ports = [port for port in QSerialPortInfo.availablePorts()]

        self.port_combo.addItems([port.portName() for port in ports])

        self.logging_timer = QTimer()
        self.logging_timer.timeout.connect(self.get_values)

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

        self.action_monitor.setReadOnly(True)
        # self.layout.setColumnStretch()

        self.horizontalLayout_3 = QHBoxLayout()
        spacerItem = QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem)
        self.pushButton_3 = QPushButton("Confirm")
        self.pushButton_3.clicked.connect(self.attodry_controller.Confirm)
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        spacerItem1 = QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushButton_2 = QPushButton("Cancel")
        self.pushButton_2.clicked.connect(self.attodry_controller.Cancel)
        self.horizontalLayout_3.addWidget(self.pushButton_2)
        spacerItem2 = QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem2)
        self.layout.addLayout(self.horizontalLayout_3, 0, 7, 1, 1)
        self.pushButton_5 = QPushButton("Activate Temperature control")
        self.layout.addWidget(self.pushButton_5, 2, 5, 1, 1)
        self.horizontalLayout = QHBoxLayout()
        self.pushButton_6 = QPushButton("Set PID")
        self.horizontalLayout.addWidget(self.pushButton_6)
        self.lineEdit_2 = QLineEdit(self)
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.lineEdit_3 = QLineEdit(self)
        self.horizontalLayout.addWidget(self.lineEdit_3)
        self.lineEdit_4 = QLineEdit(self)
        self.horizontalLayout.addWidget(self.lineEdit_4)
        self.layout.addLayout(self.horizontalLayout, 2, 7, 1, 1)
        self.pushButton_4 = QPushButton("Heat Up")
        self.pushButton_4.clicked.connect(self.attodry_controller.startSampleExchange)
        self.layout.addWidget(self.pushButton_4, 1, 5, 1, 1)
        self.lineEdit = QLineEdit(self)
        self.layout.addWidget(self.lineEdit, 2, 6, 1, 1)
        self.pushButton = QPushButton("Base Temperature")
        self.pushButton.clicked.connect(self.attodry_controller.goToBaseTemperature)
        self.layout.addWidget(self.pushButton, 0, 5, 1, 1)
        self.pushButton_7 = QPushButton("Break Sample Valve")
        self.layout.addWidget(self.pushButton_7, 1, 8, 1, 1)
        # self.pushButton_7.clicked.connect(
        #     self.attodry_controller.toggleBreakVac800Valve
        # )
        self.pushButton_7.setCheckable(True)

        self.layout.addWidget(port_label, 0, 0)
        self.layout.addWidget(self.port_combo, 0, 1)
        self.layout.addItem(spacerItem, 0, 2)
        self.layout.addWidget(self.connect_button, 0, 3)
        self.layout.addWidget(self.disconnect_button, 0, 4)
        self.layout.addWidget(self.file_locator, 1, 0, 1, 4)
        self.layout.addWidget(self.log_file_browse, 1, 4)
        self.layout.addWidget(QLabel("Logging Interval (ms)"), 2, 1)
        self.layout.addWidget(self.logging_interval_edit, 2, 2)
        self.layout.addWidget(self.stage_temp_canvas, 3, 0, 1, 5)
        self.layout.addWidget(self.stage_pressure_canvas, 4, 0, 1, 5)
        self.layout.addWidget(self.turbo_pump_canvas, 5, 0, 1, 5)
        self.layout.addWidget(self.cold_temp_canvas, 3, 5, 1, 5)
        self.layout.addWidget(self.heater_power_canvas, 4, 5, 1, 5)
        self.layout.addWidget(self.action_monitor, 5, 5, 1, 5)

        for i, plot_widget in enumerate(self.canvases):
            plot_widget.showGrid(x=True, y=True, alpha=0.5)
            plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(self.data_names[i], units="units")
            plot_widget.getAxis("bottom").setPen(pg.mkPen(color="k"))
            plot_widget.getAxis("left").setPen(pg.mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.setXRange(0, 1)

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
                        f.write(",".join(self.data_titles) + "\n")
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
            time.sleep(30)

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
        repeat = True
        while repeat:
            try:
                temperature = self.attodry_controller.getSampleTemperature()
                pressure = self.attodry_controller.getPressure800()
                lk_sample_temperature = self.attodry_controller.get4KStageTemperature()
                heat_power = self.attodry_controller.getSampleHeaterPower()
                turbo_pump_frequency = self.attodry_controller.GetTurbopumpFrequ800()

                user_temperature = self.attodry_controller.getUserTemperature()

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
                repeat = False
            except Exception as e:
                self.action_monitor.append(f"Failed to get values {e}")

    def plot_data(self, new_data_points):
        print("HERE")
        print(self.data)
        print(new_data_points)
        print(len(self.canvases))
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
            f.write(",".join(map(str, new_data_points)) + "\n")
            f.flush()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoggerInterface()
    window.setWindowTitle("Logger Interface")
    window.setGeometry(100, 20, 1500, 800)
    window.show()
    sys.exit(app.exec())
