import datetime
import os
import sys
import logging
import time

import matplotlib
from PyQt5.QtCore import QThread, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTextEdit,
    QFrame,
)
from onglabsuite.instruments.thorlabs.pm100d import PM100D
from onglabsuite.instruments.keysight.n7744c import N7744C
from pymeasure.instruments.attocube import ANC300Controller
from pyqtgraph import PlotWidget

from src.dummies.dummycontroller import DummyANC300Controller
from src.measurement.step_measurement import StepMeasurement
from src.measurement.step_optimization import OptimizationMeasurement
from src.measurement.step_measurement import PowermeterMeasurement

matplotlib.use("QtAgg")

logger = logging.getLogger(__name__)


class QTextEditHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_message = self.format(record)
        if record.levelname == "DEBUG":
            self.text_widget.append(f"<font color=grey>{log_message}</font>")
        elif record.levelname == "INFO":
            self.text_widget.append(f"<font color=#555555>{log_message}</font>")
        elif record.levelname == "WARNING":
            self.text_widget.append(f"<font color=#F1C40F>{log_message}</font>")
        elif record.levelname == "ERROR":
            self.text_widget.append(f"<font color=red>{log_message}</font>")
        elif record.levelname == "CRITICAL":
            self.text_widget.append(f"<font color=darkred><b>{log_message}</b></font>")
        else:
            self.text_widget.append(log_message)


class MeasurementApp(QMainWindow):
    measurementStarted = pyqtSignal(list)
    measurementStopped = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Measurement Plot")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.plot_button = QPushButton("Start Measurement", self)
        self.layout.addWidget(self.plot_button)

        self.stop_button = QPushButton("Stop Measurement", self)
        self.layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_experiment)
        self.stop_button.setEnabled(False)

        self.canvas = PlotWidget(title="SHOW ME THE POWAAA")

        self.layout.addWidget(self.canvas)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.log_text.ensureCursorVisible()
        # self.log_text.setStyleSheet("background-color: #555555")
        self.log_text.verticalScrollBar().rangeChanged.connect(self.change_scroll)
        self.layout.addWidget(self.log_text)

        self.plot_button.clicked.connect(self.start_measurement)

        self.thread: QThread = QThread()
        self.thread.start()
        self.experiment = OptimizationMeasurement()

        self.experiment.moveToThread(self.thread)
        self.experiment.newDataPoint.connect(self.update_plot)
        self.experiment.measurementFinished.connect(self.switch_start)

        self.measurementStarted.connect(self.experiment.measure)

        self.data = []
        self.plot_item = None
        logger.info("SETUP")

    @pyqtSlot(bool)
    def switch_start(self, value):
        self.plot_button.setEnabled(value)
        self.stop_button.setEnabled(not value)

    @pyqtSlot(int, int)
    def change_scroll(self, min, max):
        # print("cambio", min, max)
        self.log_text.verticalScrollBar().setSliderPosition(max)

    def start_measurement(self):
        self.plot_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.data = []  # Reset data
        # self.timer.start(1000)  # Update plot every 1 second
        logger.info("Connecting devices")
        # controller = ANC300Controller(
        #     adapter="TCPIP::192.168.1.2::7230::SOCKET",
        #     axisnames=["RZ", "RY", "RX", "LZ", "LY", "LX"],
        #     passwd="123456",
        # )
        controller = DummyANC300Controller(
            adapter="TCPIP::192.168.1.2::7230::SOCKET",
            axisnames=["RZ", "RY", "RX", "LZ", "LY", "LX"],
            passwd="123456",
        )
        logger.info("ANC300 connected")
        # powermeter = PM100D("USB0::0x1313::0x8078::P0024405::INSTR")
        # powermeter = PM100D("USB0::0x1313::0x8072::1916143::INSTR")
        powermeter = DummyPM100D("USB0::0x1313::0x8072::1916143::INSTR")
        powermeter = N7744C("TCPIP0::192.168.10.110::inst0::INSTR")
        devices = {"anc300": controller, "pm": powermeter}
        logger.info("Powermeter connected")

        # start the thread
        logger.info("measurement started")
        self.measurementStarted.emit(devices)

    def stop_experiment(self):
        logger.info("stopping experiment")
        self.experiment.running = False
        # self.thread.wait()

    def update_plot(self, new_data_point):  # Simulate a measurement
        self.data.append(new_data_point)
        if len(self.data) > 200:
            self.data = self.data[-200:]
        if self.plot_item is None:
            self.plot_item = self.canvas.plot(self.data)
        else:
            self.plot_item.setData(self.data)


# class RealTimePlotCanvas(FigureCanvas):
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#         super().__init__(fig)
#         self.setParent(parent)
#
#     def update_plot(self, data):
#         self.axes.clear()
#         self.axes.plot(data)
#         self.axes.set_xlabel("Time")
#         self.axes.set_ylabel("Measurement Data")
#         self.axes.grid(True)
#         self.draw()


def main():
    date = datetime.datetime.now().strftime("%Y%m%d")
    filename = os.path.expanduser(
        rf"~\Documents\MeasurementData\Ueli\OptimizationMeasurement\log\{date}_step_measurement_.log"
    )
    app = QApplication(sys.argv)
    window = MeasurementApp()

    while os.path.exists(filename):
        if filename.split("_")[-2].isdigit():
            file_ext = int(filename.split("_")[-2]) + 1
            filename = "_".join(filename.split("_")[:-2]) + f"_{file_ext}_.log"
        else:
            filename = filename[:-4] + f"0_.log"
    print(f"Log file location is {filename}")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    window_handler = QTextEditHandler(window.log_text)
    window_handler.setFormatter(formatter)
    window_handler.setLevel(logging.INFO)

    main_logger = logging.getLogger()
    main_logger.addHandler(logging.StreamHandler())
    main_logger.addHandler(window_handler)
    main_logger.addHandler(file_handler)
    main_logger.setLevel(logging.DEBUG)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
