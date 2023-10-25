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
    QHBoxLayout,
    QSpacerItem,
)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from pyqtgraph import PlotWidget
import pyqtgraph as pg

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


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()

        self.gridLayout = QGridLayout(self)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)


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

        self.stage_temp_canvas = PlotWidget(title="Sample Temperature")
        self.stage_pressure_canvas = PlotWidget(title="Sample Space Pressure")
        self.cold_temp_canvas = PlotWidget(title="Cold Plate Temperature")
        self.heater_power_canvas = PlotWidget(title="Heater Power")
        self.turbo_pump_canvas = PlotWidget(title="Turbo Pump Frequency")

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
            "Sample Temperature",
            "Sample Space Pressure",
            "Cold Plate Temperature",
            "Heater Power",
            "Turbo Pump Frequency",
        ]

        self.data = []

        self.init_ui()

        for widget in self.findChildren(QWidget):
            if widget == self.connect_button or widget == self.port_combo:
                continue
            widget.setEnabled(False)

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
        self.port_combo = QComboBox()
        self.port_combo.addItems([port.portName() for port in ports])

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

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_controller)

        self.log_file_browse = QPushButton("Start Logging")
        self.file_locator = QLineEdit()
        self.log_file_browse.clicked.connect(self.logging_manager)

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)
        self.disconnect_button.clicked.connect(self.disconnect_controller)

        self.action_monitor.setReadOnly(True)
        # self.layout.setColumnStretch()

        self.layout.addWidget(port_label, 0, 0)
        self.layout.addWidget(self.port_combo, 0, 1)
        self.layout.addWidget(self.connect_button, 0, 2)
        self.layout.addWidget(self.disconnect_button, 0, 3)
        self.layout.addWidget(self.file_locator, 1, 0, 1, 3)
        self.layout.addWidget(self.log_file_browse, 1, 3)
        self.layout.addWidget(QLabel("Logging Interval (ms)"), 2, 1)
        self.layout.addWidget(self.logging_interval_edit, 2, 2)
        self.layout.addWidget(self.stage_temp_canvas, 3, 0, 1, 4)
        self.layout.addWidget(self.stage_pressure_canvas, 4, 0, 1, 4)
        self.layout.addWidget(self.turbo_pump_canvas, 5, 0, 1, 4)
        self.layout.addWidget(self.cold_temp_canvas, 3, 4, 1, 4)
        self.layout.addWidget(self.heater_power_canvas, 4, 4, 1, 4)
        self.layout.addWidget(self.action_monitor, 5, 4, 1, 4)

        self.horizontalLayout_3 = QHBoxLayout()
        spacerItem = QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem)
        self.pushButton_3 = QPushButton("Confirm")
        self.horizontalLayout_3.addWidget(self.pushButton_3)
        spacerItem1 = QSpacerItem(
            40,
            20,
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Minimum,
        )
        self.horizontalLayout_3.addItem(spacerItem1)
        self.pushButton_2 = QPushButton("Cancel")
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
        self.layout.addWidget(self.pushButton_4, 1, 5, 1, 1)
        self.lineEdit = QLineEdit(self)
        self.layout.addWidget(self.lineEdit, 2, 6, 1, 1)
        self.pushButton = QPushButton("Base Temperature")
        self.layout.addWidget(self.pushButton, 0, 5, 1, 1)

        for i, plot_widget in enumerate(self.canvases):
            plot_widget.showGrid(x=True, y=True, alpha=0.5)
            plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(self.data_names[i], units="units")
            plot_widget.getAxis("bottom").setPen(pg.mkPen(color="k"))
            plot_widget.getAxis("left").setPen(pg.mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.setXRange(0, 1)

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
    window.setGeometry(100, 20, 1500, 800)
    window.show()
    sys.exit(app.exec())
