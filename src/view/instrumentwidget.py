import typing

from PyQt6.QtWidgets import QWidget
from PyQt6.uic.properties import QtGui


class InstrumentWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.status = ""

        self.refresh_thread = None
        self.execute_thread = None

        self.is_connected = False

    def refresh(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def connect_instrument(self, address: str) -> bool:
        raise NotImplementedError

    def disconnect_instrument(self) -> bool:
        raise NotImplementedError

    def closeEvent(self, event: typing.Optional[QtGui.QCloseEvent]) -> None:
        if self.is_connected:
            self.disconnect_instrument()
        event.accept()
