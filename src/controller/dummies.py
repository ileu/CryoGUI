from datetime import datetime
from typing import List

from src.controller._quantities import PositionQty


class DummyAMC300Controller:
    def __init__(self, ip):
        self.ip = ip

        self.axes: List[DummyAxis] = []

        self._position = 0

    def connect(self):
        for i in range(3):
            self.axes.append(DummyAxis(i))
        return True

    def disconnect(self):
        return True


class DummyAxis(PositionQty):
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

    def _move(self):
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        if elapsed_time > 3:
            self._position = self._target_position
        else:
            self._position += (
                elapsed_time / 3 * (self._target_position - self._position)
            )

    def check_moving_axis(self):
        if self._move() - self.position_m < 1e-6:
            self.set_status_axis(False)

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

    def get_target_postion(self):
        return self._target_position
