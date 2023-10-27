import sys
from onglabsuite.interfaces._windows import WindowSidebarTabs
from onglabsuite.interfaces.smaract_setup.widgets.LaserScanning import (
    LaserScanningWidget,
)
from onglabsuite.interfaces.smaract_setup.widgets.InstrumentControl import (
    InstrumentControlWidget,
)
from onglabsuite.interfaces.smaract_setup.widgets.InstrumentConnection import (
    InstrumentConnectionWidget,
)
from PyQt5 import QtWidgets
import os

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

        self.tab1 = QtWidgets.QMainWindow()
        tab1_layout = QtWidgets.QVBoxLayout()
        tab1_layout.addWidget(QtWidgets.QPushButton("HALLLOOO"))
        # tab1_layout.addWidget(CryoWidget())
        self.tab1.setLayout(tab1_layout)
        self.tabWidget.setTabText(0, "Cryo Control")

        self.tab2 = LaserScanningWidget(parent=self)
        tab2_layout = QtWidgets.QVBoxLayout()
        tab2_layout.addWidget(self.tab2)
        self.tab_2.setLayout(tab2_layout)
        self.tabWidget.setTabText(1, "Laser Scanning")

    # def instrument_connected(self, inst):
    #     self.inst_control.add_instrument_tab(inst)
    #     if type(inst).__name__ in self.tab1.PM_ALLOWED:
    #         self.tab1.boxPMChoice.addItems([inst.name + " (" + inst.address + ")"])
    #         self.tab1.boxPMChoice.adjustSize()
    #         if not self.tab1.pm:
    #             self.tab1.connect_pm(inst)
    #             self.tab1.boxPMChoice.setCurrentIndex(
    #                 self.tab1.boxPMChoice.findText(
    #                     inst.name + " (" + inst.address + ")"
    #                 )
    #             )
    #     if type(inst).__name__ in self.tab1.SAMPLE_ALLOWED:
    #         self.tab1.boxSampleChoice.addItems([inst.name + " (" + inst.address + ")"])
    #         self.tab1.boxSampleChoice.adjustSize()
    #         if not self.tab1.samplestage:
    #             self.tab1.connect_samplestage(inst)
    #             self.tab1.boxSampleChoice.setCurrentIndex(
    #                 self.tab1.boxSampleChoice.findText(
    #                     inst.name + " (" + inst.address + ")"
    #                 )
    #             )
    #     if type(inst).__name__ in self.tab1.INPUT_ALLOWED:
    #         self.tab1.boxInputChoice.addItems([inst.name + " (" + inst.address + ")"])
    #         self.tab1.boxInputChoice.adjustSize()
    #         if not self.tab1.inputstage:
    #             self.tab1.connect_inputstage(inst)
    #             self.tab1.boxInputChoice.setCurrentIndex(
    #                 self.tab1.boxInputChoice.findText(
    #                     inst.name + " (" + inst.address + ")"
    #                 )
    #             )
    #     if type(inst).__name__ in self.tab1.OUTPUT_ALLOWED:
    #         self.tab1.boxOutputChoice.addItems([inst.name + " (" + inst.address + ")"])
    #         self.tab1.boxOutputChoice.adjustSize()
    #         if not self.tab1.outputstage and not inst == self.tab1.inputstage:
    #             self.tab1.connect_outputstage(inst)
    #             self.tab1.boxOutputChoice.setCurrentIndex(
    #                 self.tab1.boxOutputChoice.findText(
    #                     inst.name + " (" + inst.address + ")"
    #                 )
    #             )
    #     if type(inst).__name__ in self.tab2.LASER_ALLOWED:
    #         self.tab2.connect_laser(inst)
    #     if type(inst).__name__ in self.tab2.PM_ALLOWED:
    #         self.tab2.connect_pm(inst)
    #     if type(inst).__name__ in self.tab3.LASER_ALLOWED:
    #         self.tab3.connect_laser(inst)
    #     if type(inst).__name__ in self.tab3.PM_ALLOWED:
    #         self.tab3.connect_pm(inst)
    #     if type(inst).__name__ in self.tab3.PM_100D_ALLOWED:
    #         self.tab3.connect_pm100D(inst)
    #
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
    # def closeEvent(self, *args, **kwargs):
    #     super(QtWidgets.QMainWindow, self).closeEvent(*args, **kwargs)
    #     if not self.tab1.pm is None:
    #         self.tab1.plotThread.terminate()
    #         self.tab1.pm_reader.kill()
    #     for addr in self.inst_connection.connected_instruments.keys():
    #         self.inst_connection.connected_instruments[addr].close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = SmaractSetupGUI()
    sys.exit(app.exec_())
