import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal, QThreadPool, QRunnable, Qt, QTimer
from PyQt6.QtGui import QValidator, QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
)


class Mover(QRunnable):
    finished = pyqtSignal()

    def __init__(self, axis, step: float, direction: str):
        super().__init__()
        self.axis = axis
        self.step = step
        self.direction = direction

    def run(self):
        print("running")
        if self.step == 2:
            time.sleep(2)
            # raise Exception("test")
        else:
            time.sleep(10)
        print("finished")
        # self.finished.emit()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("QThreadPool + QRunnable")
        self.resize(250, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.label = QLabel("Hello, World!")
        # self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        countBtn = QPushButton("Start me!")
        stopBtn = QPushButton("Stop me!")

        self.timer = QTimer()
        self.timer.timeout.connect(self.task)
        countBtn.clicked.connect(self.runTasks)
        stopBtn.clicked.connect(self.stopTask)
        # Set the layout
        self.interval = QLineEdit()
        self.interval.setValidator(QIntValidator())
        self.interval.setText("1000")

        self.interval.textChanged.connect(
            lambda: self.timer.setInterval(int(self.interval.text()))
        )

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(countBtn)
        layout.addWidget(stopBtn)
        layout.addWidget(self.interval)
        self.centralWidget.setLayout(layout)

    def runTasks(self):
        self.timer.start(1000)

    def task(self):
        print("THIS IS A TASK")

    def stopTask(self):
        self.timer.stop()


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
