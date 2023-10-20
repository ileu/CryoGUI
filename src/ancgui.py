import sys
import threading
import time
from typing import List

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QLabel,
    QFrame,
    QPushButton,
)

from src.dummies.dummycontroller import DummyANC300Controller
from src.view import OpenLoopWidget

from pymeasure.instruments.attocube import ANC300Controller

from src.view.instrumentwidget import InstrumentWidget


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
            #     adapter=address, axisnames=axis, passwd=passwd
            # )
        except:
            self.statusUpdated.emit("Connection failed")
            return False

        self.is_connected = True
        self.ancController = ancController
        self.statusUpdated.emit("Connected")
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
    main()
