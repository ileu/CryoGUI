from typing import List

from src.controller.amclib.AMC import Device
from src.controller.axis import Axis


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
