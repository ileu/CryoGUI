import random
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class DummyClosedLoopAxis:
    def __init__(self, index):
        self._position = 0
        self._target_position = 0
        self.start_time = datetime.now()
        self.index = index
        self.grounded = True
        self.movable = False

    @property
    def position_m(self):
        if self.grounded:
            self._move()
        return self._position

    @position_m.setter
    def position_m(self, pos_m):
        start_time = datetime.now()
        if start_time > self.start_time:
            self.start_time = start_time
        self._target_position = pos_m

    @property
    def target_position(self):
        return self._target_position

    @target_position.setter
    def target_position(self, pos):
        self._target_position = pos

    def get_target_position(self):
        return self._target_position

    def _move(self):
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 3:
            self._position = self._target_position
        else:
            self._position += (
                elapsed_time / 3 * (self._target_position - self._position)
            )

    def set_axis_control_move(self, b):
        print(f"{self.index} set axis control move", b)
        start_time = datetime.now()
        if b and start_time > self.start_time:
            self.start_time = datetime.now()
        self.movable = b

    def get_axis_movement(self) -> bool:
        return self.movable

    def activate_axis(self):
        print(f"{self.index} activate axis")
        self.grounded = True

    def deactivate_axis(self):
        print(f"{self.index} deactivate axis")
        self.grounded = False

    def set_status_axis(self, status):
        print(f"{self.index} set status axis", status)
        self.grounded = status

    def get_status_axis(self):
        return self.grounded


class DummyOpenLoopAxis:
    def __init__(
        self,
        title: str = "Dummy Axis",
        voltage: float = None,
        frequency: float = None,
        offset: float = None,
        capacity: float = None,
        mode: str = "GND",
    ):
        self._title = title

        self.voltage = voltage if voltage else random.randint(0, 50)
        self.frequency = frequency if frequency else random.randint(16, 1000)
        self.offset_voltage = offset if offset else random.randint(0, 50)
        self.mode = mode
        self.capacity = capacity if capacity else random.uniform(200, 300)

    def __getattr__(self, item):
        if item.startswith("_"):
            return super().__getattribute__(item)
        logger.info(f"{self._title} get {item}")
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key.startswith("_"):
            super().__setattr__(key, value)
        logger.info(f"{self._title} set {key}: {value}")
        super().__setattr__(key, value)

    def ask(self, question):
        if "c" in question:
            return self.capacity
