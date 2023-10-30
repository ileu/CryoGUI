import sys
import threading
import time
from typing import List

from PyQt5.QtCore import pyqtSignal, QThread
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
)
from pymeasure.instruments.attocube.anc300 import Axis
from pymeasure.instruments.attocube import ANC300Controller

from src.dummies.dummycontroller import DummyANC300Controller
from src.view.instrumentwidget import InstrumentWidget
from src.view import OpenLoopWidget

import logging

logger = logging.getLogger(__name__)


class ANCGUI(InstrumentWidget):
    connected = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ip_address = None
        self.ancController = None

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        self.status_label = QLabel("Disconnected")
        self.statusUpdated.connect(self.status_label.setText)

        self.axis = [
            "RZ",
            "RY",
            "RX",
            "LZ",
            "LX",
            "LY",
        ]
        self.axis_widgets = {}

        for axi in self.axis:
            ax_widget = OpenLoopWidget(title=axi, lock_optimize_on_start="Z" in axi)
            self.axis_widgets[axi] = ax_widget
            # ax_widget.deactivate()
            mainLayout.addWidget(ax_widget)

        mainLayout.addWidget(self.status_label)
        self.setLayout(mainLayout)

    def refresh(self):
        for ax_wid in self.axis_widgets.values():
            ax_wid.update()

    def execute(self):
        pass

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
        logger.info("ANC300 initialized")
        self.connected.emit(True)
        return True

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
    connect_button.clicked.connect(lambda: connect_anc(gui))
    anc_thread = QThread()

    gui.moveToThread(anc_thread)

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
