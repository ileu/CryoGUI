from typing import List

from PyQt5.QtCore import QObject, pyqtSignal

from src.controller._quantities import PositionQty
from src.controller.amclib.AMC import Device


class AMC300Controller(QObject):
    deviceConnected = pyqtSignal()
    deviceDisconnected = pyqtSignal()
    statusUpdated = pyqtSignal(str)

    def __init__(self, ip, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.ip = ip
        self.device = Device(ip)
        self.axes: List[Axis] = []

        self.connected = False

    def connect(self):
        if not self.ip:
            self.statusUpdated.emit("No IP address given")
            return False

        try:
            self.device.connect()
        except Exception as e:
            print(e)
            self.statusUpdated.emit(f"Error during connection: {e}")
            return False
        self.connected = True
        self.deviceConnected.emit()

        for i in range(3):
            self.axes.append(Axis(i, self.device, self.parent))
        self.statusUpdated.emit("Connected")
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
        self.statusUpdated.emit("Disconnected")
        self.deviceDisconnected.emit()
        return True


class Axis(QObject):
    positionUpdated = pyqtSignal(float)
    targetPositionUpdated = pyqtSignal(float)
    modeUpdated = pyqtSignal(bool)
    activivityUpdated = pyqtSignal(bool)
    valuesUpdated = pyqtSignal(list)
    statusUpdated = pyqtSignal(str)

    def __init__(self, index, device: Device, parent=None):
        """

        :param index:
        :param device:
        """
        super().__init__(parent)
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

    def update_position(self):
        """
        Updates the position of the axis
        :return:
        """
        self._position = self.device.move.getPosition(self.index) * 1e-9
        self.positionUpdated.emit(self._position * 1e6)

    def update_values(self):
        """
        Updates the values of the axis
        :return:
        """
        frequency = self.device.control.getControlFrequency(self.index) * 1e-3
        voltage = self.device.control.getControlAmplitude(self.index) * 1e-3
        offset = self.device.control.getControlFixOutputVoltage(self.index) * 1e-3
        self.valuesUpdated.emit([voltage, frequency, offset])

    def set_value(self, value: float, name: str):
        """
        Sets the value of the axis
        :param value: value to set
        :param name: name of the value to set
        :return:
        """
        print("Setting value", value, name)
        if name == "voltage":
            self.device.control.setControlAmplitude(self.index, value * 1e3)
        elif name == "frequency":
            self.device.control.setControlFrequency(self.index, value * 1e3)
        elif name == "offset":
            self.device.control.setControlFixOutputVoltage(self.index, value * 1e3)
        # self.update_values()

    def set_axis_control_move(self, b: bool):
        self.device.control.setControlMove(self.index, b)

    def get_axis_movement(self) -> bool:
        acitivity = self.device.control.getControlMove(self.index)
        self.activivityUpdated.emit(acitivity)
        return acitivity

    def set_status_axis(self, status: bool):
        self.device.control.setControlOutput(self.index, status)
        # self.modeUpdated.emit(status)

    def get_status_axis(self) -> bool:
        mode = self.device.control.getControlOutput(self.index)
        self.modeUpdated.emit(mode)
        return mode

    def set_target_position(self, pos_um: float):
        print("Setting target position", pos_um)
        self.device.move.setControlTargetPosition(self.index, pos_um * 1e3)

    def get_target_position(self):
        target_position = self.device.move.getControlTargetPosition(self.index)
        self.targetPositionUpdated.emit(target_position*1e-3)
        return target_position
