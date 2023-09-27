import typing
from abc import abstractmethod

from PyQt6.QtWidgets import QWidget
from PyQt6.uic.properties import QtGui


class InstrumentWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.status = ""

        self.is_refresh_thread_running = False
        self.refresh_thread = None

        self.is_action_thread_running = False
        self.action_thread = None

        self.is_connected = False

    @abstractmethod
    def refresh(self):
        raise NotImplementedError

    @abstractmethod
    def execute(self):
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
