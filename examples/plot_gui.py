import datetime
import sys
import random
import logging
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTextEdit,
)
import pyqtgraph as pg
from pyqtgraph import DateAxisItem


class QTextEditHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        log_message = self.format(record)
        self.text_widget.append(log_message)


class MeasurementApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time Measurement Plot with Styling")
        self.setGeometry(100, 100, 1000, 600)  # Wider window to fit 3 plots

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.plot_button = QPushButton("Start Measurement", self)
        self.layout.addWidget(self.plot_button)

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        self.layout.addWidget(self.log_text, stretch=1)

        self.plot_widgets = [pg.PlotWidget(self) for _ in range(6)]
        for plot_widget in self.plot_widgets:
            self.layout.addWidget(plot_widget, stretch=2)

        self.plot_button.clicked.connect(self.start_measurement)

        self.data = [[] for _ in range(6)]  # Create 3 lists for data
        self.times = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)

        self.logger = logging.getLogger("MeasurementAppLogger")
        log_handler = QTextEditHandler(self.log_text)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        log_handler.setFormatter(formatter)
        self.logger.addHandler(log_handler)
        self.logger.setLevel(logging.INFO)

        # Apply styling to the plot widgets
        for i, plot_widget in enumerate(self.plot_widgets):
            # if i != 0:
            #     plot_widget.setXLink(self.plot_widgets[0])
            plot_widget.showGrid(x=True, y=True, alpha=0.5)
            plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(f"Data {i+1}", units="units")
            plot_widget.getAxis("bottom").setPen(pg.mkPen(color="k"))
            axis = DateAxisItem()
            plot_widget.setAxisItems({"bottom": axis})
            plot_widget.getAxis("left").setPen(pg.mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.setXRange(0, 1)
            plot_widget.setAutoVisible(x=True)

    def start_measurement(self):
        for data in self.data:
            data.clear()
        self.timer.start(50)
        self.log_text.clear()
        self.logger.info("Measurement started.")

    def update_plot(self):
        new_data_points = [random.uniform(0, 10) for _ in range(6)]
        time = datetime.datetime.now()
        # self.times.append(time.timestamp())
        for data, data_point, plot_widget in zip(
            self.data, new_data_points, self.plot_widgets
        ):
            data.append(data_point)
            # xmax = len(data) - 1
            # xmin = 0
            # if len(data) > 20:
            #     xmin = len(data) - 20
            plot_widget.plot( y=data, clear=True, pen=pg.mkPen("b")
            )  # Blue pen
            if len(data) == 20:
                plot_widget.enableAutoRange("x", enable=1)
            # plot_widget.setXRange(xmin, xmax)

            self.logger.info(f"Measurement: {data_point:.2f}")


def main():
    app = QApplication(sys.argv)
    window = MeasurementApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
