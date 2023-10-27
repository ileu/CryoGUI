import os
import sys

from PyQt5 import QtWidgets, QtCore
from onglabsuite.interfaces._windows import WindowSidebarTabs
from onglabsuite.interfaces.smaract_setup.widgets.InstrumentConnection import (
    InstrumentConnectionWidget,
)
from onglabsuite.interfaces.smaract_setup.widgets.InstrumentControl import (
    InstrumentControlWidget,
)
from onglabsuite.interfaces.smaract_setup.widgets.LaserScanning import (
    LaserScanningWidget,
)
import pyqtgraph as pg
from pyqtgraph import PlotWidget

from src.amcgui import AMCGUI
from src.ancgui import ANCGUI
from src.cryogui import CryoWidget


class SmaractSetupGUI(WindowSidebarTabs):
    def __init__(self, parent=None):
        super(SmaractSetupGUI, self).__init__(parent)
        self.show()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        list_path = os.path.join(ui_path, "INSTRUMENT_LIST.txt")

        self.inst_connection = InstrumentConnectionWidget(list_path, parent=self)
        self.inst_control = InstrumentControlWidget(parent=self)

        # self.inst_connection.InstrumentConnected.connect(self.instrument_connected)
        # self.inst_connection.InstrumentDisconnected.connect(
        #     self.instrument_disconnected
        # )

        self.sidebar_layout = self.sidebar.layout()
        self.sidebar_layout.addWidget(self.inst_connection)
        self.sidebar_layout.addWidget(self.inst_control)

        self.cryo_widget = CryoWidget(parent=self)
        tab1_layout = QtWidgets.QVBoxLayout()
        tab1_layout.addWidget(self.cryo_widget)
        self.tab.setLayout(tab1_layout)
        self.tabWidget.setTabText(0, "Cryo Control")

        self.amc_widget = AMCGUI(parent=self)
        self.anc_widget = ANCGUI(parent=self)
        self.power_frame = QtWidgets.QFrame()
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
        t_layout = QtWidgets.QVBoxLayout()
        t_layout.setContentsMargins(0, 0, 0, 0)
        # t_layout.addWidget()
        self.power_frame.setLayout(t_layout)
        stage_layout = QtWidgets.QGridLayout()
        stage_layout.addWidget(self.anc_widget, 0, 0, 2, 1)
        stage_layout.addWidget(self.power_plot, 0, 1, 1, 1)
        stage_layout.addWidget(self.amc_widget, 1, 1, 1, 1)
        self.stage_widget = QtWidgets.QWidget()
        self.stage_widget.setLayout(stage_layout)
        self.tab2_layout = QtWidgets.QVBoxLayout()
        self.tab2_layout.addWidget(self.stage_widget)
        self.tab_2.setLayout(self.tab2_layout)
        self.tabWidget.setTabText(1, "Stage Control")

        self.laser_scanner = LaserScanningWidget(parent=self)
        tab3_layout = QtWidgets.QVBoxLayout()
        tab3_layout.addWidget(self.laser_scanner)
        self.tab_3.setLayout(tab3_layout)
        self.tabWidget.setTabText(2, "Laser Scanning")

        self.tabs = [
            self.cryo_widget,
            self.stage_widget,
            self.laser_scanner,
        ]

        self.tabWidget.setCurrentIndex(0)

    def instrument_connected(self, inst):
        self.inst_control.add_instrument_tab(inst)
        for tab in self.tabs:
            if type(inst).__name__ in self.tab.PM_ALLOWED:
                self.tab1.boxPMChoice.addItems([inst.name + " (" + inst.address + ")"])
                self.tab1.boxPMChoice.adjustSize()
                if not self.tab1.pm:
                    self.tab1.connect_pm(inst)
                    self.tab1.boxPMChoice.setCurrentIndex(
                        self.tab1.boxPMChoice.findText(
                            inst.name + " (" + inst.address + ")"
                        )
                    )
            if type(inst).__name__ in self.tab.SAMPLE_ALLOWED:
                self.tab1.boxSampleChoice.addItems(
                    [inst.name + " (" + inst.address + ")"]
                )
                self.tab1.boxSampleChoice.adjustSize()
                if not self.tab1.samplestage:
                    self.tab1.connect_samplestage(inst)
                    self.tab1.boxSampleChoice.setCurrentIndex(
                        self.tab1.boxSampleChoice.findText(
                            inst.name + " (" + inst.address + ")"
                        )
                    )
            if type(inst).__name__ in self.tab.INPUT_ALLOWED:
                self.tab1.boxInputChoice.addItems(
                    [inst.name + " (" + inst.address + ")"]
                )
                self.tab1.boxInputChoice.adjustSize()
                if not self.tab1.inputstage:
                    self.tab1.connect_inputstage(inst)
                    self.tab1.boxInputChoice.setCurrentIndex(
                        self.tab1.boxInputChoice.findText(
                            inst.name + " (" + inst.address + ")"
                        )
                    )
            if type(inst).__name__ in self.tab.OUTPUT_ALLOWED:
                self.tab1.boxOutputChoice.addItems(
                    [inst.name + " (" + inst.address + ")"]
                )
                self.tab1.boxOutputChoice.adjustSize()
                if not self.tab1.outputstage and not inst == self.tab1.inputstage:
                    self.tab1.connect_outputstage(inst)
                    self.tab1.boxOutputChoice.setCurrentIndex(
                        self.tab1.boxOutputChoice.findText(
                            inst.name + " (" + inst.address + ")"
                        )
                    )
        if type(inst).__name__ in self.laser_scanner.LASER_ALLOWED:
            self.laser_scanner.connect_laser(inst)
        if type(inst).__name__ in self.laser_scanner.PM_ALLOWED:
            self.laser_scanner.connect_pm(inst)
        if type(inst).__name__ in self.laser_scanner.PM_100D_ALLOWED:
            self.laser_scanner.connect_pm100D(inst)

    # def instrument_disconnected(self, inst):
    #     self.inst_control.remove_instrument_tab(inst.address)
    #     if type(inst).__name__ in self.tab1.PM_ALLOWED:
    #         print("disconect")
    #         self.tab1.boxPMChoice.removeItem(
    #             self.tab1.boxPMChoice.findText(inst.name + " (" + inst.address + ")")
    #         )
    #         self.tab1.disconnect_pm()
    #     if type(inst).__name__ in self.tab1.SAMPLE_ALLOWED:
    #         self.tab1.boxSampleChoice.removeItem(
    #             self.tab1.boxSampleChoice.findText(
    #                 inst.name + " (" + inst.address + ")"
    #             )
    #         )
    #     if type(inst).__name__ in self.tab1.INPUT_ALLOWED:
    #         self.tab1.boxInputChoice.removeItem(
    #             self.tab1.boxInputChoice.findText(inst.name + " (" + inst.address + ")")
    #         )
    #     if type(inst).__name__ in self.tab1.OUTPUT_ALLOWED:
    #         self.tab1.boxOutputChoice.removeItem(
    #             self.tab1.boxOutputChoice.findText(
    #                 inst.name + " (" + inst.address + ")"
    #             )
    #         )
    #     del self.inst_connection.connected_instruments[inst.address]
    #
    def closeEvent(self, *args, **kwargs):
        super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)
        if not self.stage_widget.pm is None:
            self.tab1.plotThread.terminate()
            self.tab1.pm_reader.kill()
        for addr in self.inst_connection.connected_instruments.keys():
            self.inst_connection.connected_instruments[addr].close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SmaractSetupGUI()
    sys.exit(app.exec_())
