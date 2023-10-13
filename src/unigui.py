from PyQt6.QtWidgets import (
    QMainWindow,
    QLabel,
    QStatusBar,
    QWidget,
    QGridLayout,
)
from pyqtgraph import PlotWidget


class UniGui(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.setWindowTitle("QMainWindow")

        self.graphWidget = PlotWidget()

        hour = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        temperature = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        # plot data: x, y values
        self.graphWidget.plot(hour, temperature)

        self.lay = QGridLayout(self)

        self.lay.addWidget(QLabel("I'm the Central Widget"), 1, 1)
        self.lay.addWidget(self.graphWidget, 2, 1, 1, 2)

        centralWidget = QWidget(self)
        centralWidget.setLayout(self.lay)

        self.setCentralWidget(centralWidget)
        self._createMenu()
        self._createStatusBar()

    def _createMenu(self):
        menu = self.menuBar().addMenu("&Menu")
        menu.addAction("&Exit", self.close)

        serial_menu = self.menuBar().addMenu("&Serial")
        serial_menu.addAction("&Connect...", self.close)
        serial_menu.addAction("&Disconnect", self.close)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("I'm RUNNNING")
        self.setStatusBar(status)


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    window = UniGui()
    window.show()
    sys.exit(app.exec())
