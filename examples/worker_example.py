from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal, QObject


class Master(QObject):
    command = pyqtSignal(str)

    def __init__(self):
        super().__init__()


class Worker(QObject):
    def __init__(self):
        super().__init__()

    def do_something(self, text):
        print(
            "current thread id = {}, message to worker = {}".format(
                int(QtCore.QThread.currentThreadId()), text
            )
        )


if __name__ == "__main__":
    app = QtCore.QCoreApplication([])

    # give us a thread and start it
    thread = QtCore.QThread()
    thread.start()

    # create a worker and move it to our extra thread
    worker = Worker()
    worker.moveToThread(thread)

    # create a master object and connect it to the worker
    master = Master()
    master.command.connect(worker.do_something)

    # call a method of the worker directly (will be executed in the actual thread)
    worker.do_something("wrong way to communicate with worker")

    # communicate via signals, will execute the method now in the extra thread
    master.command.emit("right way to communicate with worker")

    # start the application and kill it after 1 second
    QtCore.QTimer.singleShot(1000, app.quit)
    app.exec_()

    # don't forget to terminate the extra thread
    thread.quit()
    thread.wait(5000)
