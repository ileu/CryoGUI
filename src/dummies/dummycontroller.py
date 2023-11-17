import logging
import random
from typing import List

import numpy as np
from PyQt5.QtCore import QObject

from src.controller._quantities import PowerQty
from src.dummies.dummies import DummyOpenLoopAxis

logger = logging.getLogger(__name__)


class DummyController:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, item):
        logger.debug(f"get {item}")
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        logger.debug(f"set {key}: {value}")
        super().__setattr__(key, value)


class DummyANC300Controller(DummyController):
    def __init__(self, adapter, axisnames, passwd):
        super().__init__()
        self.adapter = adapter
        self.axisnames = axisnames
        self.passwd = passwd

        for name in self.axisnames:
            setattr(self, name, DummyOpenLoopAxis(title=name))

        self._position = 0

    def connect(self):
        for name in self.axisnames:
            self.setattr(name, DummyOpenLoopAxis(title=name))
        return True

    def disconnect(self):
        return True


class DummyAMC300Controller(DummyController, QObject):
    def __init__(self, ip):
        super().__init__()
        QObject.__init__(self)
        self.ip = ip

        self.axes: List[DummyOpenLoopAxis] = []

        self._position = 0

    def connect(self):
        for i in range(3):
            self.axes.append(DummyOpenLoopAxis(str(i)))
        return True

    def disconnect(self):
        return True


class DummyAttoDRY(DummyController):
    def __init__(self, com_port=None, **kwargs):
        super().__init__()
        self.started = False
        self.connected = False
        self.com_port = None

    def begin(self):
        self.started = True

    def end(self):
        self.started = False

    def Connect(self, com_port):
        self.connected = True
        self.com_port = com_port

    def Disconnect(self):
        self.connected = False
        self.com_port = None

    def Confirm(self):
        return True

    def Cancel(self):
        return True

    def startSampleExchange(self):
        pass

    def goToBaseTemperature(self):
        pass

    def getSampleTemperature(self):
        return random.uniform(4, 100)

    def getPressure800(self):
        return random.uniform(0, 1e-6)

    def get4KStageTemperature(self):
        return random.uniform(4, 4.4)

    def getSampleHeaterPower(self):
        return random.uniform(0, 3)

    def GetTurbopumpFrequ800(self):
        return random.uniform(0, 1200)

    def getUserTemperature(self):
        return random.uniform(273, 274)

    def isDeviceInitialised(self):
        return True

    def isDeviceConnected(self):
        return True


class DummyPM100D(PowerQty):
    def __init__(self, address, signal_width=30, signal_max_power=10):
        super().__init__()
        self.address = address
        self.signal_width = signal_width
        self.signal_max_power = signal_max_power

    @property
    def power_uW(self, position=None):
        if position is None:
            return random.normalvariate(self.signal_max_power, self.signal_width)
        return self.signal_max_power * np.exp(
            -np.power((position - position) / self.signal_width, 2.0) / 2
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test = DummyANC300Controller("test", ["LX", "LY", "LZ"], "123456")
    print(test.LX)
