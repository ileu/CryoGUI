import time

from PyQt5.QtCore import QObject, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication


class Worker(QObject):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.do_something)
        self.timer.setSingleShot(True)
        self.timer.setInterval(600)
        self.start_time = 0

    def do_something(self):
        print("** STOPPED Doing something **", time.time() - self.start_time)

    def start(self):
        if not self.timer.isActive():
            self.start_time = time.time() - self.start_time
            self.timer.start(600)
            print("STARTED Doing something", self.start_time)
        else:
            print("DOING IT", time.time() - self.start_time)
            self.timer.setInterval(150)


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = Worker()
        self.button = QPushButton("Start", self)
        self.button.clicked.connect(self.start)
        self.button.setShortcut("right")
        self.button.setAutoRepeat(True)
        self.button.setAutoRepeatDelay(100)
        self.button.setAutoRepeatInterval(100)

    def start(self):
        self.worker.start()

    def keyPressEvent(self, a0):
        if a0.nativeVirtualKey() in [65, 68, 83, 87, 98, 100, 102, 104]:
            if a0.isAutoRepeat():
                print("auto repeat")
            else:
                print("not auto repeat")


if __name__ == "__main__":
    app = QApplication([])
    window = Window()
    window.show()
    app.exec()
