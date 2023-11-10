from PyQt5.QtCore import QObject


class ANC300Controller(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
