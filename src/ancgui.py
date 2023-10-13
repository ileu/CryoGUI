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
    QLabel,
    QFrame,
)
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

        self.axis = ["LX", "LY", "LZ", "RX", "RY", "RZ"]
        self.axis_widgets = {}

        lineFrame = QFrame()
        lineFrame.setFixedSize(100, 2)
        lineFrame.setStyleSheet(
            "QFrame {border: 2px solid black; border-radius: 20px; }"
        )

        for axi in self.axis:
            ax_widget = OpenLoopWidget(title=axi)
            self.axis_widgets[axi] = ax_widget
            ax_widget.deactivate()
            mainLayout.addWidget(ax_widget)
            mainLayout.addWidget(lineFrame)

        mainLayout.addWidget(self.status_label)
        self.setLayout(mainLayout)

    def refresh(self):
        while self.is_refresh_thread_running:
            for ax_wid in self.axis_widgets.values():
                ax_wid.update()

            time.sleep(0.1)

    def execute(self):
        pass

    def connect_instrument(
        self, address: str, axis: list = None, passwd: str = "123456"
    ) -> bool:
        if axis is None:
            axis = self.axis

        try:
            pass
            ancController: ANC300Controller = (
                None  # ANC300Controller(adapter=address, axisnames=axis, passwd=passwd)
            )
        except:
            self.status = "Connection failed"
            return False

        self.is_connected = True
        self.ancController = ancController

        # self.is_refresh_thread_running = True
        # self.refresh_thread = threading.Thread(target=self.refresh())
        # self.refresh_thread.start()

        return True

    def disconnect_instrument(self) -> bool:
        pass


def main():
    app = QApplication(sys.argv)
    gui = ANCGUI()
    gui.connect_instrument("1234")
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
