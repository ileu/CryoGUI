import sys
import threading
import time

from PyQt5.QtCore import QRunnable, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QApplication, QWidget


class Worker(QRunnable):
    def __init__(self, passing_list):
        super().__init__()
        self.setAutoDelete(False)
        self.user_ids = passing_list[0]
        self.usernames = passing_list[1]

    def run(self):
        print(self.usernames, threading.get_ident())
        for i in range(10):
            now = time.strftime("%H:%M:%S")
            print(f"{i}: {self.usernames} + running: {now}")
            time.sleep(0.5)


class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI()
        self.initSignal()
        self.worker = None

    def setupUI(self):
        layout = QVBoxLayout()
        self.pb = QPushButton("Start")
        self.pb2 = QPushButton("Stop")

        layout.addWidget(self.pb)
        layout.addWidget(self.pb2)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def initSignal(self):
        self.pb.clicked.connect(self.start)

    def start(self):
        if not self.worker:
            input = ["id", "hans"]
            self.worker = Worker(input)

        for i in range(3):
            print("main", threading.get_ident())
            QThreadPool.globalInstance().start(self.worker)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())
