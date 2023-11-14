from typing import List

from src.controller._quantities import PositionQty
from src.controller.amclib.AMC import Device


class AMC300Controller:
    def __init__(self, ip):
        self.ip = ip

        self.device = Device(ip)

        self.axes: List[Axis] = []

        self.connected = False

    def connect(self):
        try:
            self.device.connect()
        except Exception as e:
            print(e)
            return False
        self.connected = True

        for i in range(3):
            self.axes.append(Axis(i, self.device))
            # self.axes[i].position()  # update the position of the axis

        return True

    def disconnect(self):
        """
        Disconnects the controller from the device

        :return: True if successful, False otherwise
        """
        for axis in self.axes:
            self.device.control.setControlOutput(axis.index, False)

        try:
            self.device.close()
            self.connected = False
        except Exception as e:
            print(e)
            return False
        return True


class Axis(PositionQty):
    def __init__(self, index, device: Device):
        """

        :param index:
        :param device:
        """
        self.index = index
        self.device = device
        self._position = 0

    @property
    def position_m(self):
        """
        Returns the position of the axis in meters
        :return:
        """
        self.update_position()
        return self._position

    @position_m.setter
    def position_m(self, pos_m):
        """
        Sets the position of the axis in meters
        :param pos_m: desired position in meters
        :return:
        """
        self._position = pos_m

        if pos_m < 2e-3 or pos_m > 10e-3:
            raise OverflowError("Position is out of axis limit")
        self.device.move.setControlTargetPosition(self.index, pos_m * 1e9)
        # allow for moving axis
        self.set_axis_control_move(True)

    def update_position(self):
        """
        Updates the position of the axis
        :return:
        """
        self._position = self.device.move.getPosition(self.index) * 1e-9

    def set_axis_control_move(self, b: bool):
        self.device.control.setControlMove(self.index, b)

    def get_axis_movement(self) -> bool:
        return self.device.control.getControlMove(self.index)

    def activate_axis(self):
        # turn on axis
        self.device.control.setControlOutput(self.index, True)

    def deactivate_axis(self):
        # deactivate axis and ground axis
        self.device.control.setControlOutput(self.index, False)

    def set_status_axis(self, status: bool):
        self.device.control.setControlOutput(self.index, status)

    def get_status_axis(self) -> bool:
        return self.device.control.getControlOutput(self.index)

    def get_target_position(self):
        return self.device.move.getControlTargetPosition(self.index)
