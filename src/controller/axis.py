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
        return self._position

    @position_m.setter
    def position_m(self, pos_m):
        """
        Sets the position of the axis in meters
        :param pos_m: desired position in meters
        :return:
        """
        self._position = pos_m

        if pos_m * 1e9 > 2 ** 47 / 1000 or pos_m < 0:
            raise OverflowError("Position is oOut of axis limit")
        self.device.move.setControlTargetPosition(self.index, pos_m * 1e9)
        self.device.control.setControlMove(self.index, True)

    def update_position(self):
        """
        Updates the position of the axis
        :return:
        """
        self._position = self.device.move.getPosition(self.index) * 1e-9
