import sys
import numpy as np
import serial
import threading
from PyQt6.QtGui import QAction
from serial.tools.list_ports import comports
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, \
    QInputDialog, QMessageBox, QFileDialog, QHBoxLayout, QStatusBar, QPlainTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.view import NumberWidget


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUI with Plots and Text Fields")
        self.setGeometry(100, 100, 1000, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QHBoxLayout(self.central_widget)

        # Create layout for the plots (left side)
        plots_layout = QVBoxLayout()
        self.figure1 = Figure()
        self.canvas1 = FigureCanvas(self.figure1)
        plots_layout.addWidget(self.canvas1)

        self.figure2 = Figure()
        self.canvas2 = FigureCanvas(self.figure2)
        plots_layout.addWidget(self.canvas2)

        self.figure3 = Figure()
        self.canvas3 = FigureCanvas(self.figure3)
        plots_layout.addWidget(self.canvas3)
        layout.addLayout(plots_layout)

        # Create layout for the rest (right side)
        self.text_fields_layout = QVBoxLayout()

        # Create text fields
        self.pressure_field = NumberWidget(title="Pressure", unit=" kPa", symbols=7)
        self.text_fields_layout.addWidget(self.pressure_field)

        self.temperature_field = NumberWidget(title="Temperature", unit=" K", symbols=9)
        self.text_fields_layout.addWidget(self.temperature_field)

        self.voltage1_field = NumberWidget(title="Voltage 1", unit=" V", symbols=9)
        self.text_fields_layout.addWidget(self.voltage1_field)

        self.voltage2_field = QLineEdit(self)
        self.voltage2_field.setPlaceholderText("Voltage 2")
        self.text_fields_layout.addWidget(self.voltage2_field)

        self.button = QPushButton("Update Plots", self)
        self.button.clicked.connect(self.update_plots)
        self.text_fields_layout.addWidget(self.button)

        self.serial_text_edit = QPlainTextEdit(self)
        self.serial_text_edit.setReadOnly(True)
        self.text_fields_layout.addWidget(self.serial_text_edit)

        layout.addLayout(self.text_fields_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        self.serial_port = None  # No initial connection
        self.measurement_running = False  # Measurement status
        self.measurement_thread = None

        self.plot()

        self.init_menu()

    def init_menu(self):
        menubar = self.menuBar()

        self.connect_action = QAction("Connect Serial Port", self)
        self.connect_action.triggered.connect(self.show_port_dialog)
        menubar.addAction(self.connect_action)

        self.disconnect_action = QAction("Disconnect Serial Port", self)
        self.disconnect_action.triggered.connect(self.disconnect_serial)
        menubar.addAction(self.disconnect_action)

        self.start_measurement_button = QAction("Start Measurement", self)
        self.start_measurement_button.triggered.connect(self.start_measurement)
        menubar.addAction(self.start_measurement_button)

    def start_measurement(self):
        if not self.measurement_running:
            if self.serial_port:
                file_path, _ = QFileDialog.getSaveFileName(self, "Save Measurement Data", "",
                                                           "CSV Files (*.csv);;All Files (*)")

                if file_path:
                    self.measurement_running = True
                    self.status_bar.showMessage("Measurement Running")

                    with open(file_path, 'w') as f:
                        f.write("Pressure,Temperature,Voltage1,Voltage2\n")  # Write header

                    self.measurement_thread = self.measure_thread(file_path)
                    self.measurement_thread.start()
                    self.start_measurement_button.setText("Stop Measurement")
        else:
            self.stop_measurement()

    def measure_thread(self, file_path):
        def thread():
            while self.measurement_running:
                data = self.serial_port.readline().decode().strip()

                self.serial_text_edit.appendPlainText(data)

                values = data.split(',')

                if len(values) == 3:
                    y1, y2, y3 = map(float, values)

                    # Update the plot data
                    self.plot1.set_ydata(y1)
                    self.plot2.set_ydata(y2)
                    self.plot3.set_ydata(y3)

                    # Redraw the plots
                    self.canvas1.draw()
                    self.canvas2.draw()
                    self.canvas3.draw()

                    # Save data to file
                    with open(file_path, 'a') as f:
                        f.write(f"{y1},{y2},{y3},\n")

        return threading.Thread(target=thread)

    def stop_measurement(self):
        self.measurement_running = False
        if self.measurement_thread:
            self.measurement_thread.join()
        self.start_measurement_button.setText("Start Measurement")
        self.status_bar.showMessage("Measurement Stopped")

    def show_port_dialog(self):
        available_ports = [port.device for port in comports()]
        port, ok = QInputDialog.getItem(self, "Select Serial Port", "Available Ports:", available_ports, editable=False)

        if ok:
            self.connect_serial(port)

    def connect_serial(self, port):
        if not self.serial_port:
            self.serial_port = serial.Serial(port, baudrate=9600, timeout=1)  # Adjust settings as needed
            self.status_bar.showMessage("Serial Connected")

    def disconnect_serial(self):
        if self.serial_port:
            confirm = QMessageBox.question(self, "Disconnect Serial Port", "Are you sure you want to disconnect?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm == QMessageBox.StandardButton.Yes:
                self.serial_port.close()
                self.serial_port = None
                self.status_bar.showMessage("Serial Disconnected")

    def plot(self):
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        y3 = np.tan(x)

        axes1 = self.figure1.add_subplot()
        self.plot1, = axes1.plot(x, y1)
        axes1.set_title("Plot 1")

        axes2 = self.figure2.add_subplot()
        self.plot2, = axes2.plot(x, y2)
        axes2.set_title("Plot 2")

        axes3 = self.figure3.add_subplot()
        self.plot3, = axes3.plot(x, y3)
        axes3.set_title("Plot 3")

        self.canvas1.draw()
        self.canvas2.draw()
        self.canvas3.draw()

    def update_plots(self):
        if self.serial_port:
            data = self.serial_port.readline().decode().strip()
            values = data.split(',')

            if len(values) == 3:
                y1, y2, y3 = map(float, values)
                self.pressure_field.setText(str(y1))
                self.temperature_field.setText(str(y2))
                self.voltage1_field.setText(str(y3))

                self.plot1.set_ydata(np.sin(y1))
                self.plot2.set_ydata(np.cos(y2))
                self.plot3.set_ydata(np.tan(y3))

                self.canvas1.draw()
                self.canvas2.draw()
                self.canvas3.draw()

    def closeEvent(self, event):
        self.disconnect_serial()  # Ensure serial port is disconnected
        event.accept()


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
