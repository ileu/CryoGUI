from PyQt5.QtWidgets import QWidget


class BaseWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def activate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(True)
        self.update()

    def deactivate(self):
        for widget in self.findChildren(QWidget):
            widget.setEnabled(False)
        self.update()
