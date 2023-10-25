import os
import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtSerialPort import QSerialPortInfo
from PyQt6.QtWidgets import (
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
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget

from src.dummies.dummycontroller import DummyAttoDRY


# from src.AttoDRY import AttoDRY, Cryostats


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


class RealTimePlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlabel("Time")
        self.axes.set_ylabel("Measurement Data")
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.updateGeometry()
        self.line = None

    def update_plot(self, data):
        self.axes.clear()
        self.axes.plot(data)
        self.axes.grid(True)
        self.draw()


class LoggerInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = None

        # self.attodry_controller = AttoDRY(
        #     setup_version=Cryostats.ATTODRY800, com_port=None
        # )

        self.attodry_controller = DummyAttoDRY()
        self.action_monitor = QTextEdit()
        self.is_connected = False

        self.stage_temp_canvas = PlotWidget()
        self.stage_temp_canvas.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        self.stage_pressure_canvas = PlotWidget()
        self.stage_pressure_canvas.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        self.cold_temp_canvas = PlotWidget()
        self.cold_temp_canvas.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        self.heater_power_canvas = PlotWidget()
        self.heater_power_canvas.plot([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        self.init_ui()

        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.read_and_log_data)
        # self.log_file = None

    def init_ui(self):
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        port_label = QLabel("Port")
        self.layout.addWidget(port_label, 0, 0)
        ports = [port for port in QSerialPortInfo.availablePorts()]
        self.port_combo = QComboBox()
        self.port_combo.addItems([port.portName() for port in ports])
        self.layout.addWidget(self.port_combo, 0, 1)

        self.logging_timer = QTimer(
            self,
        )
        self.logging_timer.timeout.connect(self.log)

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
        self.layout.addWidget(self.logging_interval_edit, 2, 2)
        self.layout.addWidget(QLabel("Logging Interval (ms)"), 2, 1)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_controller)
        self.layout.addWidget(self.connect_button, 0, 2)

        self.log_file_browse = QPushButton("Start Logging")
        self.file_locator = QLineEdit()
        self.log_file_browse.clicked.connect(self.logging_manager)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_controller)

        self.layout.addWidget(self.disconnect_button, 0, 3)
        self.layout.addWidget(self.file_locator, 1, 0, 1, 3)
        self.layout.addWidget(self.log_file_browse, 1, 3)
        self.action_monitor.setReadOnly(True)
        self.layout.addWidget(self.action_monitor, 3, 0, 1, 4)
        self.layout.addWidget(self.stage_temp_canvas, 4, 0, 1, 4)
        self.layout.addWidget(self.stage_pressure_canvas, 5, 0, 1, 4)
        self.layout.addWidget(self.cold_temp_canvas, 6, 0, 1, 4)
        self.layout.addWidget(self.heater_power_canvas, 7, 0, 1, 4)

    def logging_manager(self, running: bool = False):
        if not running:
            dialog = QFileDialog(self)
            dialog.setDirectory(os.path.join(os.path.dirname(__file__)))
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setViewMode(QFileDialog.ViewMode.List)

            filenames, ok = dialog.getSaveFileName(
                self, "Save File", "", "Text Files (*.txt);; CSV (*.csv)"
            )
            if ok and filenames:
                self.file_locator.setText(filenames)

                self.log_file_browse.setText("Stop Logging")
                self.logging_timer.start(1000)
                self.logging_interval_edit.setEnabled(True)
            else:
                self.log_file_browse.setChecked(False)
        else:
            self.log_file_browse.setText("Start Logging")
            self.logging_timer.stop()
            # self.log_file.close()
            # self.log_file = None

    def log(self):
        print("logging", self.logging_timer.interval())

    def connect_controller(self, serial_port: str = None):
        if serial_port is None:
            serial_port = self.port_combo.currentText()
        try:
            self.attodry_controller.begin()
            self.attodry_controller.Connect(serial_port)
            # time.sleep(30)

            # self.timer.start(1000)  # Read data every second
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.action_monitor.append(f"Connected to serial port {serial_port}")
        except Exception as e:
            self.action_monitor.append(f"Failed to connect to serial port: {str(e)}")

    def disconnect_controller(self):
        try:
            self.attodry_controller.Disconnect()
            self.attodry_controller.end()

            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.action_monitor.append(f"Disconnected from serial port")
            # self.timer.stop()
        except Exception as e:
            self.action_monitor.append(
                f"Failed to disconnect from serial port: {str(e)}"
            )

    def update_plot(self, new_data_point):  # Simulate a measurement
        self.data.append(new_data_point)
        self.canvas.update_plot(self.data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoggerInterface()
    window.setWindowTitle("Logger Interface")
    window.setGeometry(100, 20, 600, 800)
    window.show()
    sys.exit(app.exec())
