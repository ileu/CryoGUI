from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QFrame

import pyqtgraph as pg
from pyqtgraph import PlotWidget

from src.amcgui import AMCGUI
from src.ancgui import ANCGUI


class CouplingWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.amc_widget = AMCGUI(parent=self)
        self.anc_widget = ANCGUI(parent=self)

        self.power_frame = QFrame()
        self.power_frame.setStyleSheet("border: 1px solid lightgray;")

        self.power_plot = PlotWidget(
            title="SHOW ME THE POWAAA", parent=self.power_frame
        )
        self.power_plot.setYRange(-1, 1)
        self.power_plot.showGrid(x=True, y=True, alpha=0.5)
        self.power_plot.getAxis("bottom").setLabel("Time", units="s")
        self.power_plot.getAxis("left").setLabel("POWER", units="W")
        self.power_plot.getAxis("bottom").setPen(pg.mkPen(color="k"))
        self.power_plot.getAxis("left").setPen(pg.mkPen(color="k"))
        self.power_plot.showAxis("right")
        self.power_plot.getAxis("right").setStyle(showValues=False)
        self.power_plot.getAxis("right").setPen(pg.mkPen(color="k"))
        self.power_plot.showAxis("top")
        self.power_plot.getAxis("top").setStyle(showValues=False)
        self.power_plot.getAxis("top").setPen(pg.mkPen(color="k"))
        self.power_plot.setBackground("w")
        self.power_plot.setXRange(0, 1)

        t_layout = QVBoxLayout ()
        t_layout.setContentsMargins(0, 0, 0, 0)

        self.power_frame.setLayout(t_layout)
        stage_layout = QGridLayout()
        stage_layout.addWidget(self.anc_widget, 0, 0, 2, 1)
        stage_layout.addWidget(self.power_plot, 0, 1, 1, 1)
        stage_layout.addWidget(self.amc_widget, 1, 1, 1, 1)

        self.setLayout(stage_layout)
