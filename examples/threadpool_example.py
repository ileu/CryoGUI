import sys
import time

from PyQt6.QtCore import QThread, pyqtSignal, QThreadPool, QRunnable, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
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
        countBtn = QPushButton("Click me!")
        countBtn.clicked.connect(self.runTasks)
        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(countBtn)
        self.centralWidget.setLayout(layout)

    def runTasks(self):
        threadCount = QThreadPool.globalInstance().maxThreadCount()
        self.label.setText(f"Running {threadCount} Threads")
        pool = QThreadPool.globalInstance()
        for i in range(threadCount):
            # 2. Instantiate the subclass of QRunnable
            runnable = Mover(i, i, "left")
            # 3. Call start()
            pool.start(runnable)


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())
