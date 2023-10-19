from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class DummyOpenLoopAxis:
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
        print("set axis control move", b)
        start_time = datetime.now()
        if b and start_time > self.start_time:
            self.start_time = datetime.now()
        self.movable = b

    def get_axis_movement(self) -> bool:
        return self.movable

    def activate_axis(self):
        print("activate axis")
        self.grounded = True

    def deactivate_axis(self):
        print("deactivate axis")
        self.grounded = False

    def set_status_axis(self, status):
        print("set status axis", status)
        self.grounded = status

    def get_status_axis(self):
        return self.grounded


class DummyClosedLoopAxis:
    def __init__(
        self,
        voltage: float = 0,
        frequency: float = 0,
        offset: float = 0,
        step: float = 0,
        status: str = "GND",
    ):
        self.voltage = voltage
        self.frequency = frequency
        self.offset = offset
        self.step = step
        self.status = status

    def __getattr__(self, item):
        logger.info(f"get {item}")
        return super().__getattribute__(item)

    def __setattr__(self, key, value):
        logger.info(f"set {key}: {value}")
        super().__setattr__(key, value)
