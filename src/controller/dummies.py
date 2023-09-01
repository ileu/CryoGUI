from datetime import datetime
from typing import List

from src.controller._quantities import PositionQty


class DummyAMC300Controller:
    def __init__(self, ip):
        self.ip = ip

        self.axes: List[DummyPosQty] = []

        self._position = 0

    def connect(self):
        for i in range(3):
            self.axes.append(DummyPosQty(i))
        return True

    def disconnect(self):
        return True


class DummyPosQty(PositionQty):
    def __init__(self, index):
        self._position = 0
        self.start_time = datetime.now()
        self.index = index
        self.active = False
        self.moving = False

    @property
    def position_m(self):
        return self._move()

    @position_m.setter
    def position_m(self, pos_m):
        self.start_time = datetime.now()
        self._position = pos_m

    def _move(self):
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 6:
            return self._position
        else:
            return self._position * elapsed_time / 6

    def check_moving_axis(self):
        if self._move() - self.position_m < 1e-6:
            self.disable_axis_movement()

    def enable_axis_movement(self):
        self.moving = True

    def disable_axis_movement(self):
        self.moving = False

    def get_axis_movement(self) -> bool:
        return self.moving

    def activate_axis(self):
        self.active = True

    def deactivate_axis(self):
        self.active = False
