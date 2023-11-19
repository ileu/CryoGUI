import datetime
import os
import sys
import time
from typing import List

from PyQt5.QtCore import QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtSerialPort import QSerialPortInfo
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QFileDialog,
    QGridLayout,
    QLabel,
    QComboBox,
    QTextEdit,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QDoubleSpinBox,
)
from pyqtgraph import PlotWidget, mkPen, DateAxisItem

from src.controller.attodry800 import AttoDry800Controller
from src.workers import LogWorker


class CryoWidget(QWidget):
    disconnectReady = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.serial_port = None

        self.action_monitor = QTextEdit()
        self.port_combo = QComboBox()
        self.connect_button = QPushButton("Connect")

        self.stage_temp_canvas = PlotWidget(title="Sample Temperature")
        self.stage_pressure_canvas = PlotWidget(title="Sample Space Pressure")
        self.cold_temp_canvas = PlotWidget(title="Cold Plate Temperature")
        self.heater_power_canvas = PlotWidget(title="Heater Power")
        self.turbo_pump_canvas = PlotWidget(title="Turbo Pump Frequency")

        self.user_temperature = 4

        self.p_value = 0
        self.i_value = 0
        self.d_value = 0

        self.plot_widgets: List[PlotWidget] = [
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
        self.colors = ["r", "b", "r", "g", "g"]
        data_titles = [
            "sample-temp_K",
            "sample-pres_mbar",
            "cold-plate-temp_K",
            "heater-power_W",
            "turbo-pump-freq_Hz",
        ]

        # self.plot_thread = QThread()
        #
        # self.plot_worker = PlotWorker(self.plot_widgets, self, data_names, data_units)
        # self.plot_worker.moveToThread(self.plot_thread)

        self.log_thread = QThread()
        self.log_worker = LogWorker("", self, data_titles)
        self.log_worker.moveToThread(self.log_thread)

        self.data = [[] for i in range(5)]
        self.time = []
        self.user_temperature = 4

        self.controller_thread = QThread()
        self.controller = AttoDry800Controller()
        self.controller.moveToThread(self.controller_thread)

        self.init_ui()

        for widget in self.findChildren((QPushButton, QLineEdit)):
            if widget == self.connect_button or widget == self.port_combo:
                continue
            widget.setEnabled(False)

        self.port_combo.currentTextChanged.connect(self.controller.set_port)

        self.update_timer = QTimer()
        self.update_timer.setInterval(50)
        self.update_timer.timeout.connect(self.controller.update_values)

        self.connect_button.clicked.connect(self.controller.connect_attodry)
        self.connect_button.clicked.connect(self.connect_button.setEnabled)
        self.disconnect_button.clicked.connect(self.update_timer.stop)
        self.disconnect_button.clicked.connect(self.controller.disconnect_attodry)
        self.base_temperature_button.clicked.connect(
            self.controller.attodry.goToBaseTemperature
        )

        self.controller.updatedValues.connect(self.plot_data)
        self.controller.statusUpdated.connect(self.action_monitor.append)
        self.controller.connectedToInstrument.connect(self.connect_controller)
        self.controller.disconnectedInstrument.connect(self.disconnect_controller)

        self.port_combo.currentTextChanged.connect(self.controller.set_port)
        self.controller.set_port(self.port_combo.currentText())

        self.controller_thread.finished.connect(self.controller.end_controller)
        self.controller_thread.finished.connect(self.controller_thread.deleteLater)
        self.controller_thread.finished.connect(self.controller.deleteLater)
        self.controller_thread.start()

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        setup_layout = QGridLayout()
        ports = [port for port in QSerialPortInfo.availablePorts()]

        self.port_combo.addItems([port.portName() for port in ports])

        self.logging_interval_edit = QLineEdit("1000")
        self.logging_interval_edit.setToolTip("Needs to be bigger than 100ms")
        # self.logging_interval_edit.editingFinished.connect(
        #     lambda: self.logging_timer.setInterval(
        #         int(self.logging_interval_edit.text())
        #     )
        # )
        self.logging_interval_edit.inputRejected.connect(
            lambda: print("rejected", self.logging_interval_edit.hasAcceptableInput())
        )

        self.logging_interval_edit.setValidator(QIntValidator(bottom=500))
        self.logging_interval_edit.editingFinished.connect(
            lambda: self.logging_interval_edit.setStyleSheet(
                "background-color: red"
                if int(self.logging_interval_edit.text()) < 100
                else "background-color: white"
            )
        )
        self.logging_interval_edit.setEnabled(False)

        self.log_file_browse = QPushButton("Start Logging")
        self.log_file_browse.clicked.connect(self.logging_manager)
        self.log_file_browse.setCheckable(True)

        self.file_locator = QLineEdit()

        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setEnabled(False)

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
            self.controller.attodry.goToBaseTemperature
        )
        self.base_temperature_button.clicked.connect(
            lambda: self.log_worker.add_remark("Going to base temperature")
        )

        controller_layout.addWidget(self.base_temperature_button, 0, 0)

        self.heat_up_button = QPushButton("Heat Up")
        self.heat_up_button.clicked.connect(self.controller.attodry.startSampleExchange)
        self.heat_up_button.clicked.connect(
            lambda: self.log_worker.add_remark("Heating up")
        )
        controller_layout.addWidget(self.heat_up_button, 1, 0)

        self.temperature_control_button = QPushButton("Activate Temperature control")
        # self.temperature_control_button.clicked.connect(
        #     self.controller.attodry.toggleTemperatureControl
        # )
        self.temperature_control_button.clicked.connect(
            lambda: self.log_worker.add_remark("Toggling temperature control")
        )
        controller_layout.addWidget(self.temperature_control_button, 2, 0)

        self.user_temperature_edit = QDoubleSpinBox()
        self.user_temperature_edit.setRange(4, 300)
        self.user_temperature_edit.setDecimals(2)
        self.user_temperature_edit.setSuffix(" K")
        self.user_temperature_edit.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.user_temperature_edit.setValue(self.user_temperature)
        self.user_temperature_edit.editingFinished.connect(
            lambda: self.log_worker.addedRemark.emit(
                f"Set User Temperature to: {self.user_temperature_edit.text()} K"
            )
        )
        self.user_temperature_edit.setEnabled(False)
        controller_layout.addWidget(self.user_temperature_edit, 2, 1)

        self.set_pid_button = QPushButton("Set PID")
        controller_layout.addWidget(self.set_pid_button, 2, 2)


        self.p_edit = QDoubleSpinBox()
        controller_layout.addWidget(self.p_edit, 2, 3)
        self.p_edit.setEnabled(False)

        self.i_edit = QDoubleSpinBox()
        controller_layout.addWidget(self.i_edit, 2, 4)
        self.i_edit.setEnabled(False)

        self.d_edit = QDoubleSpinBox()
        controller_layout.addWidget(self.d_edit, 2, 5)
        self.d_edit.setEnabled(False)

        self.break_valve_button = QPushButton("Break Sample Valve")
        # self.break_valve_button.clicked.connect(
        #     self.controller.attodry.toggleBreakVac800Valve
        # )
        controller_layout.addWidget(self.break_valve_button, 0, 5)

        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.clicked.connect(self.controller.attodry.Confirm)
        self.confirm_button.clicked.connect(
            lambda: self.log_worker.add_remark("Confirmed")
        )
        controller_layout.addWidget(self.confirm_button, 0, 3)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.controller.attodry.Cancel)
        self.cancel_button.clicked.connect(
            lambda: self.log_worker.add_remark("Cancelled")
        )
        controller_layout.addWidget(self.cancel_button, 0, 4)

        for i, plot_widget in enumerate(self.plot_widgets):
            plot_widget.showGrid(x=True, y=True, alpha=0.1)
            plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(
                self.data_names[i] + f" / {self.data_units[i]}"
            )
            plot_widget.getAxis("bottom").setPen(mkPen(color="k"))
            plot_widget.getAxis("left").setPen(mkPen(color="k"))
            plot_widget.showAxis("right")
            plot_widget.getAxis("right").setStyle(showValues=False)
            plot_widget.getAxis("right").setPen(mkPen(color="k"))
            plot_widget.showAxis("top")
            plot_widget.getAxis("top").setStyle(showValues=False)
            plot_widget.getAxis("top").setPen(mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.getPlotItem().setContentsMargins(0, 0, 25, 10)
            plot_widget.enableAutoRange(x=True, y=True)
            # plot_widget.setStyleSheet(
            #     "border: 0px solid gray; border-radius: 5px; padding: 2px; background-color: white"
            # )
            plot_widget.setStyleSheet(
                "QFrame {background-color: white; border: 2px solid black;}"
            )
            # put datetime axis as xaxis
            datetime_axis = DateAxisItem(orientation="bottom")
            datetime_keys = list(datetime_axis.zoomLevels.keys())
            datetime_axis.zoomLevels[datetime_keys[-1]] = datetime_axis.zoomLevels[datetime_keys[-2]]
            plot_widget.getPlotItem().setAxisItems({"bottom": datetime_axis})
            if i != 0:
                plot_widget.setXLink(self.plot_widgets[0])

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
            self.action_monitor.append(f"Log file path: {filename}")
            if filename:
                self.log_worker.set_filename(filename)
                self.file_locator.setText(filename)
                self.log_file_browse.setText("Stop Logging")
                self.controller.updatedValues.connect(self.log_worker.update)
                self.file_locator.setEnabled(False)
                self.logging_interval_edit.setEnabled(True)
                self.action_monitor.append(f"Started logging to {filename}")
                self.log_thread.start()
            else:
                self.log_file_browse.setChecked(False)
        else:
            self.log_file_browse.setText("Start Logging")
            self.file_locator.setEnabled(True)

            self.action_monitor.append(f"Logging stopped")
            self.controller.updatedValues.disconnect(self.log_worker.update)
            self.log_thread.exit()
            self.log_thread.wait()
            # self.log_file.close()
            # self.log_file = None

    def connect_controller(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)
        self.connect_button.setEnabled(False)

        # self.plot_thread.start()
        self.update_timer.start()

    def disconnect_controller(self):
        try:
            for widget in self.findChildren((QPushButton, QLineEdit)):
                if widget == self.connect_button or widget == self.port_combo:
                    continue
                widget.setEnabled(False)
            self.connect_button.setEnabled(True)
            self.action_monitor.append(f"Disconnected from instrument")
        except Exception as e:
            self.action_monitor.append(
                f"Failed to disconnect from serial port: {str(e)}"
            )

    def plot_data(self, new_data_points):
        self.time.append(time.time())
        for i, data, data_point, plot_widget in zip(
            range(len(new_data_points)), self.data, new_data_points, self.plot_widgets
        ):
            # print(data)
            item = plot_widget.getPlotItem()
            data.append(data_point)
            if len(data) > 4e4:
                data.pop(0)
            item.plot(self.time, data, clear=True, pen=mkPen(color=self.colors[i]))

    def closeEvent(self, *args, **kwargs):
        super().closeEvent(*args, **kwargs)
        print("closing")
        self.update_timer.stop()
        time.sleep(.5)

        # self.plot_thread.exit()
        # self.plot_thread.wait()
        # print("plot thread closed")

        self.log_thread.exit()
        self.log_thread.wait()
        print("log thread closed")

        self.controller_thread.exit()
        self.controller_thread.wait()
        print("controller thread closed")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CryoWidget()
    window.setWindowTitle("Logger Interface")
    window.setGeometry(100, 20, 1500, 800)
    window.show()
    sys.exit(app.exec())
