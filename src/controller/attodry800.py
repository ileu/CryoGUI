import time

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread

from src.AttoDRY import Cryostats

try:
    from src.AttoDRY import AttoDRY
except Exception as e:
    print(f"Failed to import AttoDRY {e}")
    from src.dummies.dummycontroller import DummyAttoDRY as AttoDRY

import logging

logger = logging.getLogger(__name__)


class AttoDry800Controller(QObject):
    updatedValues = pyqtSignal(object)
    pidValues = pyqtSignal(list)
    failedRequest = pyqtSignal(str)
    connectedToInstrument = pyqtSignal()
    disconnectedInstrument = pyqtSignal()
    statusUpdated = pyqtSignal(str)

    def __init__(self, setup_version=Cryostats.ATTODRY800, com_port=None):
        super().__init__()
        self.attodry = AttoDRY(setup_version=setup_version, com_port=com_port)
        self.value_getters = [
            self.attodry.getSampleTemperature,
            self.attodry.getPressure800,
            self.attodry.get4KStageTemperature,
            self.attodry.getSampleHeaterPower,
            self.attodry.GetTurbopumpFrequ800,
            self.attodry.getUserTemperature,
        ]
        self.has_begun = False
        # self.refresh_thread = QThread()
        # self.refresh_thread.start()

        # self.refresh_timer = QTimer()
        # self.refresh_timer.setInterval(1000)
        # self.refresh_timer.timeout.connect(self.update_values)
        #
        # self.refresh_timer.moveToThread(self.refresh_thread)
        #
        # self.refresh_timer.start()
        self.port = com_port

    def set_port(self, port):
        self.port = port

    def sendCommand(self, command, **kwargs):
        try:
            atto_command = getattr(self, command)
            atto_answer = atto_command(kwargs)
            return atto_answer
        except Exception as e:
            print(f"Something went wrong {e}")
            return False

    def update_values(self):
        data = []
        for getter in self.value_getters:
            for i in range(4):
                try:
                    data.append(getter())
                    break
                except Exception as e:
                    logger.warning(f"Something went wrong {e}")
                    self.failedRequest.emit(str(e))
                    time.sleep(0.05)
            else:
                logger.error(f"Failed to get value {getter}")
                self.failedRequest.emit(f"Failed to get value {getter}")
                data.append(0.0)

        self.updatedValues.emit(data)

    def update_pid_values(self):
        try:
            pid_values = [
                self.attodry.getPvalue(),
                self.attodry.getIValue(),
                self.attodry.getDValue(),
            ]
            self.pidValues.emit(pid_values)
        except Exception as e:
            logger.warning(f"Somthing went wrong {e}")
            self.failedRequest.emit(str(e))

    def connect_attodry(self):
        com_port = self.port
        self.statusUpdated.emit(f"Connecting to serial port {com_port}")
        # try:
        self.attodry.begin()
        self.has_begun = True
        self.attodry.Connect(com_port)

        # you need to wait for initialization; if you just start sending
        # commands, the connection will be lost.
        time.sleep(15.0)
        self.statusUpdated.emit(f"Connecting....")
        for i in range(5):
            try:
                initialized = self.attodry.isDeviceInitialised()
                connected = self.attodry.isDeviceConnected()
                break
            except Exception as e:
                print(f"Something went wrong {e}")
                time.sleep(5)
        else:
            self.statusUpdated.emit(f"Failed to connect to serial port {com_port}")
            return False
        # state that it is initialized and connected:
        if initialized and connected:
            self.statusUpdated.emit("The AttoDRY device is initialized and connected")
        else:
            self.statusUpdated.emit("something went wrong.")
            return False
        self.statusUpdated.emit(f"Connected to serial port {com_port}")
        # self.refresh_timer.start(1000)
        self.connectedToInstrument.emit()
        return True
        # except Exception as e:
        #     self.statusUpdated.emit(f"Failed to connect to serial port: {str(e)}")
        #     print(e)
        # return False

    def disconnect_attodry(self):
        self.statusUpdated.emit("Disconnecting...")
        # self.refresh_timer.stop()
        time.sleep(1.5)
        self.attodry.Disconnect()

        self.disconnectedInstrument.emit()
        return True

    def end_controller(self):
        if not self.has_begun:
            return
        print("Ending the controller")
        time.sleep(0.5)
        self.attodry.end()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from src.AttoDRY import Cryostats
    from src.AttoDRY import AttoDRY

    app = QApplication(sys.argv)
    atto = AttoDry800Controller(setup_version=Cryostats.ATTODRY800)
    atto.connect_attodry()
    sys.exit(app.exec_())
