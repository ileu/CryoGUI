import sys
import time

from PyQt6 import QtCore
from PyQt6.QtCore import QTimer
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
)

from src.controller.dummies import DummyAttoDRY


# from src.AttoDRY import AttoDRY, Cryostats


class LoggerInterface(QMainWindow):
    def __init__(self):
        super().__init__()

        self.serial_port = None

        # self.attodry_controller = AttoDRY(
        #     setup_version=Cryostats.ATTODRY800, com_port=None
        # )

        self.attodry_controller = DummyAttoDRY()
        self.action_monitor = QTextEdit()

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

        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_to_serial)
        self.layout.addWidget(connect_button, 0, 2)

        self.action_monitor.setReadOnly(True)
        self.layout.addWidget(self.action_monitor, 1, 0, 1, 3)

    def connect_to_serial(self, serial_port: str = None):
        if serial_port is None:
            serial_port = self.port_combo.currentText()
        try:
            self.attodry_controller.begin()
            self.attodry_controller.Connect(serial_port)
            # time.sleep(30)

            # self.timer.start(1000)  # Read data every second
        except Exception as e:
            self.action_monitor.append(f"Failed to connect to serial port: {str(e)}")

    def read_and_log_data(self):
        if self.serial_port:
            data = self.serial_port.readline().decode("utf-8")
            self.text_edit.append(data.strip())

            if self.log_file is not None:
                self.log_file.write(data)

    def save_log(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save Log File",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options,
        )
        if file_name:
            try:
                self.log_file = open(file_name, "w")
            except Exception as e:
                self.text_edit.append(f"Failed to save log file: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoggerInterface()
    window.setWindowTitle("Logger Interface")
    window.setGeometry(100, 100, 600, 400)
    window.show()
    sys.exit(app.exec())
