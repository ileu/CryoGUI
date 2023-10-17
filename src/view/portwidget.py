import sys
import threading
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QDialog,
    QComboBox,
    QPushButton,
    QLineEdit,
    QFileDialog,
)
from PyQt6.QtGui import QImage, QPixmap, QIcon, QAction
from PyQt6.QtCore import QTimer
from serial.tools.list_ports import comports


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Camera Feed with PyQt")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout(self.central_widget)
        self.label = QLabel(self)
        layout.addWidget(self.label)

        # self.camera = cv2.VideoCapture(0)  # Open the default camera (change index for other cameras)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.update_frame)
        # self.timer.start(30)  # Set the update interval in milliseconds

        self.start_measurement_button = None
        self.stop_measurement_button = None
        self.measurement_running = False

        self.init_menu()

    # def update_frame(self):
    #     ret, frame = self.camera.read()
    #     if ret:
    #         # rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #         h, w, ch = rgb_frame.shape
    #         bytes_per_line = ch * w
    #         q_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #         pixmap = QPixmap.fromImage(q_image)
    #         self.label.setPixmap(pixmap)

    def init_menu(self):
        menubar = self.menuBar()
        connect_serial_action = QAction("Connect to Serial Port", self)
        connect_serial_action.triggered.connect(self.show_port_dialog)
        menubar.addAction(connect_serial_action)

        self.start_measurement_button = QAction(
            QIcon("start_icon.png"), "Start Measurement", self
        )
        self.start_measurement_button.triggered.connect(self.start_measurement)
        menubar.addAction(self.start_measurement_button)

        self.stop_measurement_button = QAction(
            QIcon("stop_icon.png"), "Stop Measurement", self
        )
        self.stop_measurement_button.triggered.connect(self.stop_measurement)
        self.stop_measurement_button.setDisabled(
            True
        )  # Initially disable the Stop Measurement button
        menubar.addAction(self.stop_measurement_button)

    def start_measurement(self):
        if not self.measurement_running:
            if self.serial_port:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Measurement Data",
                    "",
                    "CSV Files (*.csv);;All Files (*)",
                )

                if file_path:
                    self.measurement_running = True
                    self.status_bar.showMessage("Measurement Running")
                    with open(file_path, "w") as f:
                        f.write(
                            "Pressure,Temperature,Voltage1,Voltage2\n"
                        )  # Write header

                    self.measurement_thread = self.start_measurement_thread(file_path)
                    self.measurement_thread.start()
                    self.start_measurement_button.setDisabled(
                        True
                    )  # Disable the Start Measurement button
                    self.stop_measurement_button.setEnabled(
                        True
                    )  # Enable the Stop Measurement button

    def stop_measurement(self):
        if self.measurement_running:
            # ... (stop measurement code)

            self.start_measurement_button.setEnabled(
                True
            )  # Enable the Start Measurement button
            self.stop_measurement_button.setDisabled(
                True
            )  # Disable the Stop Measurement button
            self.measurement_running = False

    def start_measurement_thread(self, file_path):
        def measurement_thread():
            while self.measurement_running:
                data = self.serial_port.readline().decode().strip()
                values = data.split(",")

                if len(values) == 4:
                    pressure, temperature, voltage1, voltage2 = map(float, values)

                    # ... (update plots, save data to file)

        return threading.Thread(target=measurement_thread)

    def show_port_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Connect to Serial Port")
        dialog.setModal(True)

        layout = QVBoxLayout()

        port_label = QLabel("Port:")
        port_combo = QComboBox(dialog)
        ports = [port.device for port in comports()]
        port_combo.addItems(ports)
        port_layout = QVBoxLayout()
        port_layout.addWidget(port_label)
        port_layout.addWidget(port_combo)

        ip_label = QLabel("IP Address:")
        ip_edit = QLineEdit(dialog)
        ip_layout = QVBoxLayout()
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(ip_edit)

        connect_button = QPushButton("Connect", dialog)
        connect_button.clicked.connect(
            lambda: self.connect_serial(port_combo.currentText(), ip_edit.text())
        )
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(connect_button)

        layout.addLayout(port_layout)
        layout.addLayout(ip_layout)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)
        dialog.exec()

    def connect_serial(self, port, ip_address):
        pass

    def disconnect_serial(self):
        if self.serial_port:
            self.serial_port.close()
            self.serial_port = None
            self.status_bar.showMessage("Serial Disconnected")
            self.disconnect_button.setEnabled(False)  # Disable the Disconnect button

    def closeEvent(self, event):
        self.camera.release()
        if self.serial_port:
            self.serial_port.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    camera_app = GUI()
    camera_app.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
