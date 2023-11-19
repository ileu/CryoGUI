import sys
import threading
import time
from typing import List

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QInputDialog,
)
from src.widgets import ClosedLoopWidget

from controller import AMC300Controller


from src.dummies.dummycontroller import DummyAMC300Controller as AMC300Controller


class AMCGUI(QWidget):
    statusUpdated = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.ip_address = None
        self.controller = AMC300Controller("")
        mainlayout = QVBoxLayout()

        self.axis_widgets: List[ClosedLoopWidget] = []
        axis_title = ["X-Axis", "Y-Axis", "Z-Axis"]

        for i in range(3):
            self.axis_widgets.append(
                ClosedLoopWidget(title=axis_title[i], unit=r" um", symbols=7)
            )

        for ax in self.axis_widgets:
            ax.deactivate()
            mainlayout.addWidget(ax)

        self.setLayout(mainlayout)

    def show_connect_dialog(self):
        ipaddress, ok = QInputDialog.getText(
            self, "Connect to AMC300", "IP Address", text="192.168.1.1"
        )

        if ok and ipaddress:
            self.connect(ipaddress)
            self.update_thread_running = True
            self.update_thread = threading.Thread(target=self.update_positions)
            self.update_thread.start()

    def connect(self, ip_address):
        self.ip_address = ip_address
        self.controller.ip = ip_address
        #
        # if not connected:
        #     self.statusUpdated.emit("Connection failed to " + ip_address)
        #     self.is_connected = False
        #     return

        self.statusUpdated.emit("Connected to " + ip_address)
        self.is_connected = True
        self.connect_action.setEnabled(False)
        self.disconnect_action.setEnabled(True)

        for i, ax_wid in enumerate(self.axis_widgets):
            axis = self.amcController.axes[i]
            ax_wid.positionqty = axis
            ax_wid.gnd_button.setChecked(axis.get_status_axis())
            ax_wid.setStatus("Connected")
            ax_wid.activate()

    def disconnect(self):
        self.update_thread_running = False
        if self.update_thread is not None:
            self.update_thread.join()
            self.update_thread = None
        self.amcController.disconnect()

        self.statusUpdated.emit("Disconnected")
        self.is_connected = False

        self.disconnect_action.setEnabled(False)
        self.connect_action.setEnabled(True)

        for i, ax_wid in enumerate(self.axis_widgets):
            ax_wid.positionqty = None
            ax_wid.setStatus("Disconnected")
            ax_wid.deactivate()

    def update_positions(self):
        while self.update_thread_running:
            for ax_wid in self.axis_widgets:
                ax_wid.update()

            time.sleep(0.1)

    def closeEvent(self, event):
        if self.is_connected:
            self.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    gui = AMCGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
