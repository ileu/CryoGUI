import time

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread

from src.AttoDRY import Cryostats, AttoDRY
from src.dummies.dummycontroller import DummyAttoDRY

import logging

logger = logging.getLogger(__name__)


class AttoDry800Controller(QObject):
    updatedValues = pyqtSignal(list)
    pidValues = pyqtSignal(list)
    failedRequest = pyqtSignal(str)
    connectedToInstrument = pyqtSignal()
    statusUpdated = pyqtSignal(str)

    def __init__(self, setup_version=Cryostats.ATTODRY800, com_port=None):
        super().__init__()
        self.attodry = DummyAttoDRY()
        self.value_getters = [
            self.attodry.getSampleTemperature,
            self.attodry.getPressure800,
            self.attodry.get4KStageTemperature,
            self.attodry.getSampleHeaterPower,
            self.attodry.GetTurbopumpFrequ800,
            self.attodry.getUserTemperature,
        ]
        self.refresh_thread = QThread()
        self.refresh_thread.start()

        self.refresh_timer = QTimer()
        self.refresh_timer.setInterval(1000)
        self.refresh_timer.timeout.connect(self.update_values)

        self.refresh_timer.moveToThread(self.refresh_thread)

        self.refresh_timer.start()

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
            try:
                data.append(getter())
            except Exception as e:
                logger.warning(f"Something went wrong {e}")
                self.failedRequest.emit(str(e))

        self.updatedValues.emit(data)

        # for i in range(4):
        #     try:
        #         temperature = self.attodry_controller.getSampleTemperature()
        #         pressure = self.attodry_controller.getPressure800()
        #         lk_sample_temperature = self.attodry_controller.get4KStageTemperature()
        #         heat_power = self.attodry_controller.getSampleHeaterPower()
        #         turbo_pump_frequency = self.attodry_controller.GetTurbopumpFrequ800()
        #
        #         user_temperature = self.attodry_controller.getUserTemperature()
        #
        #         self.updatedUserTemperature.emit(user_temperature)
        #
        #         data = [
        #             temperature,
        #             pressure,
        #             lk_sample_temperature,
        #             heat_power,
        #             turbo_pump_frequency,
        #         ]
        #
        #         self.user_temperature = user_temperature
        #
        #         self.updatedData.emit(data)
        #         break
        #     except Exception as e:
        #         self.action_monitor.append(f"Failed to get values {e}")
        #         self.action_monitor.append(f"Retrying {4-i} times in 1 second")
        #         time.sleep(1)

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

    def connect_attodry(self, com_port=None):
        if com_port is None:
            com_port = "COM1"
        self.statusUpdated.emit(f"Connecting to serial port {com_port}")
        try:
            self.attodry.begin()
            self.attodry.Connect(com_port)

            # you need to wait for initialization; if you just start sending
            # commands, the connection will be lost.
            time.sleep(10.0)

            initialized = self.attodry.isDeviceInitialised()
            connected = self.attodry.isDeviceConnected()

            # state that it is initialized and connected:
            if initialized and connected:
                print("The AttoDRY device is initialized and connected")
            else:
                print("something went wrong.")
                return False
            self.statusUpdated.emit(f"Connected to serial port {com_port}")
            self.connectedToInstrument.emit()
            return True
        except Exception as e:
            self.statusUpdated.emit(f"Failed to connect to serial port: {str(e)}")
            print(e)
        return False

    def disconnect_attodry(self):
        self.attodry.Disconnect()
        self.attodry.end()

        time.sleep(1)

        return True
