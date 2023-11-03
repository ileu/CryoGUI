import sys
import threading
import time
from typing import List

from PyQt5.QtCore import pyqtSignal, QThread, QObject, QTimer, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QLabel,
    QFrame,
    QPushButton,
    QAction,
    QLineEdit,
    QHBoxLayout,
    QRadioButton,
    QGridLayout,
    QButtonGroup,
)
from pymeasure.instruments.attocube.anc300 import Axis
from pymeasure.instruments.attocube import ANC300Controller

from src.dummies.dummycontroller import DummyANC300Controller
from src.view.instrumentwidget import InstrumentWidget
from src.view import OpenLoopWidget

import logging

logger = logging.getLogger(__name__)


class WorkerThread(QThread):
    finished = pyqtSignal()


class ANCGUI(InstrumentWidget):
    connected = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ip_address = None
        self.ancController = None
        self.setObjectName("ANC300")

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        buttonLayout = QGridLayout()
        self.gnd_all_button = QPushButton("Ground All")
        self.gnd_all_button.clicked.connect(self.ground_all)

        temp_group = QButtonGroup(self)
        self.coarse_optimize_button = QRadioButton("Coarse Optimize")
        self.coarse_optimize_button.setChecked(True)
        self.fine_optimize_button = QRadioButton("Fine Optimize")

        temp_group.addButton(self.coarse_optimize_button)
        temp_group.addButton(self.fine_optimize_button)

        optimize_group = QButtonGroup(self)
        self.low_temp_button = QRadioButton("Low Temp")
        self.high_temp_button = QRadioButton("High Temp")
        self.high_temp_button.setChecked(True)

        optimize_group.addButton(self.low_temp_button)
        optimize_group.addButton(self.high_temp_button)

        buttonLayout.addWidget(self.high_temp_button, 0, 0)
        buttonLayout.addWidget(self.low_temp_button, 0, 1)
        buttonLayout.addWidget(self.gnd_all_button, 0, 2)
        buttonLayout.addWidget(self.coarse_optimize_button, 1, 0)
        buttonLayout.addWidget(self.fine_optimize_button, 1, 1)

        mainLayout.addLayout(buttonLayout)

        self.axis = [
            "RZ",
            "RY",
            "RX",
            "LZ",
            "LY",
            "LX",
        ]
        self.axis_widgets = {}

        for axi in self.axis:
            ax_widget = OpenLoopWidget(title=axi, lock_optimize_on_start="Z" in axi)
            self.axis_widgets[axi] = ax_widget
            # ax_widget.deactivate()
            mainLayout.addWidget(ax_widget)

        self.setLayout(mainLayout)
        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(500)
        self.refresh_timer.timeout.connect(self.refresh)

    def refresh(self):
        for ax_wid in self.axis_widgets.values():
            ax_wid.controller.update_values()
            ax_wid.controller.update_mode()

    def connect_instrument(
        self, address: str = None, axis: list = None, passwd: str = "123456"
    ) -> bool:
        if not address:
            address, ok = QInputDialog.getText(
                self,
                "ANC300 IP Address",
                "Enter IP address:",
                QLineEdit.Normal,
                "TCPIP::192.168.1.2::7230::SOCKET",
            )
            if not ok:
                return False
        logger.info(f"Connecting to ANC300 on {address}")
        if axis is None:
            axis = self.axis

        try:
            ancController = DummyANC300Controller(
                adapter=address, axisnames=axis, passwd=passwd
            )
            # ancController: ANC300Controller = ANC300Controller(
            #     adapter=address, axisnames=axis, passwd=passwd
            # )
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.statusUpdated.emit(f"Connection failed: {e}")
            return False

        logger.info("Connected to ANC300")
        self.ancController = ancController
        self.statusUpdated.emit("Connected")

        for axis_widget in self.axis_widgets.values():
            axis_widget.connect_axis(getattr(ancController, axis_widget.title))
            axis_widget.activate()

        self.axis_widgets["LX"].connect_keys("a", "d")
        self.axis_widgets["LY"].connect_keys("w", "s")
        self.axis_widgets["RX"].connect_keys("left", "right")
        self.axis_widgets["RY"].connect_keys("up", "down")

        logger.info("ANC300 initialized")
        self.refresh_timer.start()
        self.connected.emit(True)
        return True

    def ground_all(self):
        if self.ancController is None:
            return

        for axis in self.axis_widgets.values():
            axis.controller.update_mode("gnd")

    def disconnect_instrument(self) -> bool:
        pass


def main():
    app = QApplication(sys.argv)
    gui = ANCGUI()

    window = QMainWindow()
    central_widget = QWidget()
    central_widget.setLayout(QHBoxLayout())
    v_layout = QVBoxLayout()
    connect_button = QPushButton("Connect")
    connect_button.clicked.connect(gui.connect_instrument)

    mode_button = QPushButton("Mode")
    # mode_button.clicked.connnect(lambda: gui.axis_widgets["RZ"].)
    v_layout.addWidget(connect_button)
    v_layout.addWidget(mode_button)
    central_widget.layout().addLayout(v_layout)
    central_widget.layout().addWidget(gui)
    window.setCentralWidget(central_widget)

    window.show()
    sys.exit(app.exec())


def connect_anc(ancwidget: ANCGUI):
    ancwidget.connect_instrument("")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
