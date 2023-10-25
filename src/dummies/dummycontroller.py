import logging
from typing import List

from pymeasure.instruments.attocube import ANC300Controller

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


class DummyAMC300Controller(DummyController):
    def __init__(self, ip):
        super().__init__()
        self.ip = ip

        self.axes: List[DummyOpenLoopAxis] = []

        self._position = 0

    def connect(self):
        for i in range(3):
            self.axes.append(DummyOpenLoopAxis(i))
        return True

    def disconnect(self):
        return True


class DummyAttoDRY(DummyController):
    def __init__(self):
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test = DummyANC300Controller("test", ["LX", "LY", "LZ"], "123456")
    print(test.LX)
