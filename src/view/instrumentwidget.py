import typing
from abc import abstractmethod, ABC

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget


class InstrumentWidget(QWidget):
    statusUpdated = pyqtSignal(str)
    connectionChanged = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status = ""

        self.is_connected = False

    @abstractmethod
    def refresh(self):
        raise NotImplementedError

    @abstractmethod
    def connect_instrument(self, address: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def disconnect_instrument(self) -> bool:
        raise NotImplementedError

    def activate_widgets(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)

    def deactivate_widgets(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(False)

    def closeEvent(self, event) -> None:
        if self.is_connected:
            self.disconnect_instrument()
        event.accept()
