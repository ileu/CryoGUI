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
from src.view import NumberWidget

# from controller import AMC300Controller
from controller.dummies import DummyAMC300Controller as AMC300Controller


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ip_address = None
        self.amcController = None

        self.setWindowTitle("AMC300 Controller GUI")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Create main layout
        mainlayout = QVBoxLayout(self.central_widget)
        self.statusBar().showMessage("Disconnected")

        self.axis_widgets: List[NumberWidget] = []

        for i in range(3):
            self.axis_widgets.append(
                NumberWidget(title=f"Axis {i}", unit=r" um", symbols=7)
            )

        for ax in self.axis_widgets:
            ax.deactivate()
            mainlayout.addWidget(ax)

        self.init_menu()

        self.update_thread = None
        self.update_thread_running = False
        self.is_connected = False

    def init_menu(self):
        menubar = self.menuBar()

        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self.show_connect_dialog)
        menubar.addAction(connect_action)

        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect)
        menubar.addAction(disconnect_action)

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
        self.amcController = AMC300Controller(ip_address)
        self.amcController.connect()

        self.statusBar().showMessage("Connected to " + ip_address)
        self.is_connected = True

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

        self.statusBar().showMessage("Disconnected")
        self.is_connected = False

        for i, ax_wid in enumerate(self.axis_widgets):
            ax_wid.positionqty = None
            ax_wid.setStatus("Disconnected")
            ax_wid.deactivate()

    def update_positions(self):
        while self.update_thread_running:
            for ax_wid in self.axis_widgets:
                ax_wid.updateNumberDisplay()
                ax_wid.positionqty.set_status_axis(ax_wid.gnd_button.isChecked())
                ax_wid.status_label.setText(
                    "Status: " + str(ax_wid.positionqty.get_status_axis())
                )

            time.sleep(0.1)

    def closeEvent(self, event):
        if self.is_connected:
            self.disconnect()
        event.accept()


def main():
    app = QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
