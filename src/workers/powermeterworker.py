from PyQt5.QtCore import QObject


class PowerMeterWorker(QObject):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
