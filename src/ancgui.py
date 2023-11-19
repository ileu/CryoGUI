import sys

from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QInputDialog,
    QPushButton,
    QLineEdit,
    QHBoxLayout,
    QRadioButton,
    QGridLayout,
    QButtonGroup,
)
from pymeasure.instruments.attocube import ANC300Controller

from src.controller.openloopcontroller import OpenLoopController
from src.dummies.dummycontroller import DummyANC300Controller
from src.widgets.instrumentwidget import InstrumentWidget
from src.widgets import OpenLoopWidget

import logging

logger = logging.getLogger(__name__)


class ANCGUI(InstrumentWidget):
    connected = pyqtSignal(bool)
    refresh = pyqtSignal()

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

        self.low_temp_button.setEnabled(False)
        self.high_temp_button.setEnabled(False)
        self.fine_optimize_button.setEnabled(False)
        self.coarse_optimize_button.setEnabled(False)
        self.gnd_all_button.setEnabled(False)

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

        self.controller_thread = QThread()

        for axi in self.axis:
            controller = OpenLoopController(axis=None)
            controller.moveToThread(self.controller_thread)
            ax_widget = OpenLoopWidget(
                title=axi, controller=controller, lock_optimize_on_start="Z" in axi
            )
            self.axis_widgets[axi] = ax_widget
            mainLayout.addWidget(ax_widget)

        self.setLayout(mainLayout)
        self.controller_thread.start()

        # self.refresh_timer = QTimer()
        # self.refresh_timer.setInterval(10000)
        # self.refresh_timer.timeout.connect(self.refresh.emit)

    def connect_instrument_over_address(
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
            # ancController = DummyANC300Controller(
            #     adapter=address, axisnames=axis, passwd=passwd
            # )
            ancController: ANC300Controller = ANC300Controller(
                adapter=address, axisnames=axis, passwd=passwd
            )
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.statusUpdated.emit(f"Connection failed: {e}")
            return False

        logger.info("Connected to ANC300")
        return self.connect_anc(ancController)

    def connect_anc(
        self,
        anc_controller: ANC300Controller,
    ):
        self.ancController = anc_controller
        self.statusUpdated.emit("Connected")

        for axis_widget in self.axis_widgets.values():
            axis_widget.connect_axis(getattr(anc_controller, axis_widget.title))
            axis_widget.activate()
            self.refresh.connect(axis_widget.controller.refresh)

        self.coarse_optimize_button.setEnabled(True)
        self.fine_optimize_button.setEnabled(True)
        self.low_temp_button.setEnabled(True)
        self.high_temp_button.setEnabled(True)
        self.gnd_all_button.setEnabled(True)

        # self.axis_widgets["LX"].connect_keys("a", "d")
        # self.axis_widgets["LY"].connect_keys("w", "s")
        # self.axis_widgets["RX"].connect_keys("right", "left")
        # self.axis_widgets["RY"].connect_keys("down", "up")

        logger.info("ANC300 initialized")
        self.refresh.emit()
        self.connected.emit(True)
        # self.refresh_timer.start()
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
    connect_button.clicked.connect(gui.connect_instrument_over_address)

    mode_button = QPushButton("Mode")
    # mode_button.clicked.connnect(lambda: gui.axis_widgets["RZ"].)
    v_layout.addWidget(connect_button)
    v_layout.addWidget(mode_button)
    central_widget.layout().addLayout(v_layout)
    central_widget.layout().addWidget(gui)
    window.setCentralWidget(central_widget)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
