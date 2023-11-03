import os
import sys

import onglabsuite
from PyQt5 import QtWidgets, QtCore
from onglabsuite.instruments.keysight.n7744c import N7744C
from onglabsuite.instruments.keysight.n7776c import N7776C
from onglabsuite.instruments.thorlabs.pm100d import PM100D
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
from pymeasure.instruments.attocube import ANC300Controller
from pyqtgraph import PlotWidget

from src.amcgui import AMCGUI
from src.ancgui import ANCGUI
from src.controller import AMC300Controller
from src.couplingwidget import CouplingWidget
from src.cryogui import CryoWidget


class CryoSetup(WindowSidebarTabs):
    def __init__(self, parent=None):
        super(CryoSetup, self).__init__(parent)
        self.show()

        ui_path = os.path.dirname(os.path.abspath(__file__))
        list_path = os.path.join(ui_path, "view/INSTRUMENT_LIST.txt")

        self.inst_connection = InstrumentConnectionWidget(list_path, parent=self)
        self.inst_connection.instrument_classes = {
            "PM100D": PM100D,
            "N7744C": N7744C,
            "N7776C": N7776C,
            "ANC300Controller": ANC300Controller,
            "AMC300Controller": AMC300Controller,
        }
        self.inst_connection.InstrumentConnected.connect(self.instrument_connected)
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

        self.stage_widget = CouplingWidget()
        tab2_layout = QtWidgets.QVBoxLayout()
        tab2_layout.addWidget(self.stage_widget)
        self.tab_2.setLayout(tab2_layout)
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

    def keyPressEvent(self, event):
        print(event.key())
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        print(event.key())
        super().keyReleaseEvent(event)

    def instrument_connected(self, inst):
        self.inst_control.add_instrument_tab(inst)
        for tab in self.tabs:
            if type(inst).__name__ in self.tab.PM_ALLOWED:
                self.tab.boxPMChoice.addItems([inst.name + " (" + inst.address + ")"])
                self.tab.boxPMChoice.adjustSize()
                if not self.tab.pm:
                    self.tab.connect_pm(inst)
                    self.tab.boxPMChoice.setCurrentIndex(
                        self.tab.boxPMChoice.findText(
                            inst.name + " (" + inst.address + ")"
                        )
                    )
            if type(inst).__name__ in self.tab.SAMPLE_ALLOWED:
                self.tab.boxSampleChoice.addItems(
                    [inst.name + " (" + inst.address + ")"]
                )
                self.tab.boxSampleChoice.adjustSize()
                if not self.tab.samplestage:
                    self.tab.connect_samplestage(inst)
                    self.tab.boxSampleChoice.setCurrentIndex(
                        self.tab.boxSampleChoice.findText(
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
    window = CryoSetup()
    sys.exit(app.exec_())
