import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QGridLayout,
    QWidget,
    QApplication,
    QComboBox,
    QLineEdit,
    QLabel,
    QDoubleSpinBox,
)
from pyqtgraph import PlotWidget
import pyqtgraph as pg

from src.amcgui import AMCGUI
from src.ancgui import ANCGUI


class StageGui(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.amc_widget = AMCGUI()
        self.anc_widget = ANCGUI()
        self.power_frame = QFrame()
        self.power_plot = PlotWidget(title="SHOW ME THE POWAAA")

        self.power_meter = None

        self.power_meter_box = QComboBox()
        self.power_meter_channel_box = QComboBox()
        self.power_meter_channel_box.setEnabled(False)

        self.power_meter_box.addItem("Choose Instrument")

        self.power_meter_channel_box.addItem("Choose Channel")
        self.power_meter_channel_box.addItem("Channel 1")
        self.power_meter_channel_box.addItem("Channel 2")

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

        self.init_ui()

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

        self.power_plot.setYRange(-1, 1)
        self.power_plot.showGrid(x=True, y=True, alpha=0.5)
        self.power_plot.getAxis("bottom").setLabel("Time", units="s")
        self.power_plot.getAxis("left").setLabel("POWER", units="W")
        self.power_plot.getAxis("bottom").setPen(pg.mkPen(color="k"))
        self.power_plot.getAxis("left").setPen(pg.mkPen(color="k"))
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
