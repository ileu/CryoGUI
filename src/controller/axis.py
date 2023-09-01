from src.controller._quantities import PositionQty
from src.controller.amclib.AMC import Device


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
        self.check_moving_axis()
        return self._position

    @position_m.setter
    def position_m(self, pos_m):
        """
        Sets the position of the axis in meters
        :param pos_m: desired position in meters
        :return:
        """
        self._position = pos_m

        if pos_m * 1e9 > 2**47 / 1000 or pos_m < 2e-3 or pos_m > 10e-3:
            raise OverflowError("Position is oOut of axis limit")
        self.device.move.setControlTargetPosition(self.index, pos_m * 1e9)
        # allow for moving axis
        self.enable_axis_movement()

    def update_position(self):
        """
        Updates the position of the axis
        :return:
        """
        self._position = self.device.move.getPosition(self.index) * 1e-9

    def check_moving_axis(self):
        if self.device.status.getStatusTargetRange(self.index):
            self.disable_axis_movement()

    def enable_axis_movement(self):
        self.device.control.setControlMove(self.index, True)

    def disable_axis_movement(self):
        # stop the position control of the axis
        self.device.control.setControlMove(self.index, False)

    def get_axis_movement(self) -> bool:
        return self.device.control.getControlMove(self.index)

    def activate_axis(self):
        # turn on axis
        self.device.control.setControlOutput(self.index, True)

    def deactivate_axis(self):
        # deactivate axis and ground axis
        self.device.control.setControlOutput(self.index, False)
