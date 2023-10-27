import sys
import threading
import time
from typing import List

from PyQt5.QtCore import pyqtSignal
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
)
from pymeasure.instruments.attocube.anc300 import Axis
from pymeasure.instruments.attocube import ANC300Controller

from src.dummies.dummycontroller import DummyANC300Controller
from src.view.instrumentwidget import InstrumentWidget
from src.view import OpenLoopWidget

import logging

logger = logging.getLogger(__name__)


class ANCGUI(InstrumentWidget):
    def __init__(self):
        super().__init__()
        self.ip_address = None
        self.ancController = None

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        self.status_label = QLabel("Disconnected")
        self.statusUpdated.connect(self.status_label.setText)

        self.connect_button = QPushButton("Connect", self)
        self.connect_button.clicked.connect(self.connect_instrument)
        mainLayout.addWidget(self.connect_button)

        self.axis = ["LX", "LY", "LZ", "RX", "RY", "RZ"]
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
        self, address: str, axis: list = None, passwd: str = "123456"
    ) -> bool:
        if axis is None:
            axis = self.axis

        try:
            ancController = DummyANC300Controller(
                adapter=address, axisnames=axis, passwd=passwd
            )
            # ancController: ANC300Controller = ANC300Controller(
            #     adapter=address, axisnames=axis, passwdw=passwd
            # )
        except Exception as e:
            self.statusUpdated.emit(f"Connection failed: {e}")
            return False

        self.is_connected = True
        self.ancController = ancController
        self.statusUpdated.emit("Connected")
        for axis_widget in self.axis_widgets.values():
            axis_widget.axis = getattr(ancController, axis_widget.title)
            axis_widget.activate()
        self.activate_widgets()
        return True

    def disconnect_instrument(self) -> bool:
        pass


def main():
    app = QApplication(sys.argv)
    gui = ANCGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
