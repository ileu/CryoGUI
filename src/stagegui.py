import sys

import numpy as np
from PyQt5.QtCore import QThread, QTimer, pyqtSignal, QEventLoop, QThreadPool
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QApplication,
    QComboBox,
    QLabel,
    QDoubleSpinBox,
)
from onglabsuite.interfaces.smaract_setup.widgets.WaveguideCoupling import (
    PowermeterReader,
)
from pyqtgraph import PlotWidget

from src.amcgui import AMCGUI
from src.ancgui import ANCGUI
from src.workers import PlotWorker


class StageGui(QWidget):
    updatePlot = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.amc_widget = AMCGUI()
        self.anc_widget = ANCGUI()
        self.power_frame = QFrame()
        self.power_plot = PlotWidget(title="SHOW ME THE POWER")

        self.power_meter = None
        self.last_power = 0
        self.PM_ALLOWED = ["PM100D", "N7744C"]
        self.power_array = np.array([])

        self.threadPool = QThreadPool.globalInstance()

        self.power_meter_box = QComboBox()
        self.power_meter_channel_box = QComboBox()
        self.power_meter_channel_box.setEnabled(False)

        self.power_meter_box.addItem("Choose Instrument")

        self.power_meter_channel_box.addItem("Choose Channel")
        self.power_meter_channel_box.addItem("Channel 1")
        self.power_meter_channel_box.addItem("Channel 2")
        self.power_meter_channel_box.currentTextChanged.connect(self.change_channel)

        self.power_meter_rate = QDoubleSpinBox()
        self.power_meter_rate.setSuffix(" Hz")
        self.power_meter_rate.setDecimals(0)
        self.power_meter_rate.setRange(1, 1000)
        self.power_meter_rate.setValue(20)
        self.power_meter_rate.setButtonSymbols(QDoubleSpinBox.NoButtons)

        self.power_meter_wavelength = QDoubleSpinBox()
        self.power_meter_wavelength.setSuffix(" nm")
        self.power_meter_wavelength.setDecimals(2)
        self.power_meter_wavelength.setRange(0, 2000)
        self.power_meter_wavelength.setValue(1550.0)
        self.power_meter_wavelength.setButtonSymbols(QDoubleSpinBox.NoButtons)

        # t_layout = QVBoxLayout()
        # t_layout.setContentsMargins(0, 0, 0, 0)
        # # t_layout.addWidget()
        # self.power_frame.setLayout(t_layout)

        self.plot_thread = QThread()
        self.plot_worker = PlotWorker([self.power_plot], self, ["Power"], ["W"])
        self.plot_worker.moveToThread(self.plot_thread)
        self.updatePlot.connect(self.plot_worker.update)

        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.plot_tick)
        self.plot_timer.setInterval(int(1000 / self.power_meter_rate.value()))

        # self.power_meter_controller.updatedValues.connect(self.plot_worker.update)

        self.plot_thread.start()

        self.init_ui()

    def plot_tick(self):
        if self.power_meter:
            if hasattr(self.power_meter, "instrument"):
                wait = self.power_meter.instrument.waiting
            else:
                wait = self.power_meter.waiting
            if not wait:
                self.updatePower()
                self.updatePlot.emit([self.power_array])
            else:
                loop = QEventLoop()
                QTimer.singleShot(2000, loop.quit)
                loop.exec()

    def updatePower(self):
        pow_curr = self.last_power
        self.power_array = np.append(self.power_array, pow_curr)
        # datapoints = len(self.power_array)
        # if datapoints > self.datapoints:
        #     self.power_array = self.power_array[-int(self.datapoints):]

    def connect_pm(self, pm, channel=0):
        if hasattr(pm, "is_multichannel") and pm.is_multichannel:
            if channel == 1:
                pm = pm.ch2
            elif channel == 0:
                pm = pm.ch1
            elif channel == 2:
                pm = pm.ch3
            else:
                pm = pm.ch4

        self.power_meter = pm

        if hasattr(self.power_meter, "instrument"):
            self.power_meter.instrument.waiting = False
        else:
            self.power_meter.waiting = False

        # self.plot_timer.start()

        # if self.outputstage:
        #     self._enable_optimize_buttons(type=self.cpl_type['out'], side='out')
        # if self.inputstage:
        #     self._enable_optimize_buttons(type=self.cpl_type['in'], side='in')

        # self.plotWorker = PlotWorker(self.mplWidget, self)
        # self.updatePlot.connect(self.plotWorker.update)
        # self.rescalePlot.connect(self.plotWorker.rescale_y)
        # self.plotWorker.moveToThread(self.plotThread)

        if not hasattr(self, "pm_reader"):
            self.pm_reader = PowermeterReader(self.power_meter)
            self.pm_reader.signal.currentPower.connect(
                lambda value: self.__setattr__("last_power", value)
            )
            self.threadPool.start(self.pm_reader)
        else:
            self.pm_reader.pm = self.power_meter
            self.pm_reader.initialize()

        # self.plotThread.start()

    def disconnect_pm(self):
        self.plot_thread.exit()
        self.pm_reader.kill()
        self.power_meter = None

    def change_channel(self, identifier):
        # print(identifier)
        # identifier2 = self.power_meter_channel_box.currentText()
        # address = identifier2[identifier2.find("(") + 1 : -1]
        pm = self.power_meter
        self.disconnect_pm()

        if identifier == "Channel 1":
            channel = 0
        else:
            channel = 1
        self.connect_pm(pm, channel=channel)

    def init_ui(self):
        self.power_frame.setObjectName("power_frame")
        self.power_frame.setStyleSheet(
            "#power_frame {border: 2px solid lightgray; background-color: white;}"
        )
        self.power_frame.setLayout(QVBoxLayout())

        power_setting_layout = QGridLayout()
        power_setting_layout.setSpacing(5)
        power_setting_layout.addWidget(QLabel("Update Rate"), 0, 0)
        power_setting_layout.addWidget(self.power_meter_rate, 0, 1)
        power_setting_layout.addWidget(QLabel("Wavelength"), 0, 2)
        power_setting_layout.addWidget(self.power_meter_wavelength, 0, 3)
        power_setting_layout.setColumnStretch(4, 1)
        power_setting_layout.addWidget(self.power_meter_box, 0, 5)
        power_setting_layout.addWidget(self.power_meter_channel_box, 0, 6)
        self.power_frame.layout().addLayout(power_setting_layout)
        self.power_frame.layout().addWidget(self.power_plot)

        # self.power_plot.setYRange(-1, 1)
        self.power_plot.showGrid(x=True, y=True, alpha=0.1)
        # self.power_plot.getAxis("bottom").setLabel("Time", units="s")
        # self.power_plot.getAxis("left").setLabel("POWER", units="W")
        # self.power_plot.getAxis("bottom").setPen(pg.mkPen(color="k"))
        # self.power_plot.getAxis("left").setPen(pg.mkPen(color="k"))
        # self.power_plot.showAxis("right")
        # self.power_plot.getAxis("right").setStyle(showValues=False)
        # self.power_plot.getAxis("right").setPen(pg.mkPen(color="k"))
        # self.power_plot.showAxis("top")
        # self.power_plot.getAxis("top").setStyle(showValues=False)
        # self.power_plot.getAxis("top").setPen(pg.mkPen(color="k"))
        self.power_plot.setBackground("w")
        self.power_plot.setXRange(0, 1)

        stage_layout = QGridLayout()
        stage_layout.addWidget(self.anc_widget, 0, 0, 2, 1)
        stage_layout.addWidget(self.power_frame, 0, 1, 1, 1)
        stage_layout.addWidget(self.amc_widget, 1, 1, 1, 1)

        self.setLayout(stage_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StageGui()
    window.show()
    sys.exit(app.exec())
