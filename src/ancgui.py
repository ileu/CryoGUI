import sys
import threading
import time
from typing import List

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)
from src.view import OpenLoopWidget

from pymeasure.instruments.attocube import ANC300Controller


class GUI(QWidget):
    def __init__(self):
        super().__init__()
        self.ip_address = None
        self.ancController = None

        self.setWindowTitle("ANC300 Controller GUI")

        self.mainlayout = QVBoxLayout()

        self.status = "Disconnected"

        self.axis_widgets: List[OpenLoopWidget] = []

        for i in range(7):
            self.axis_widgets.append(
                OpenLoopWidget(title=f"Axis {i}", unit=r" um", symbols=7)
            )

        for ax in self.axis_widgets:
            ax.deactivate()
            self.mainlayout.addWidget(ax)

        self.update_thread = None
        self.update_thread_running = False
        self.is_connected = False

    def connect(self, ip_address):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
