from src.controller._quantities import PositionQty


# from amclib.AMC import Device


# # REDO
class ANC300Controller(PositionQty):
    def __init__(self, ip):
        self.ip = ip

#         self.device = Device(ip)
#
#         self._position = 0
#
#     def connect(self):
#         raise NotImplementedError
#
#     @property
#     def position_m(self):
#         return self._position
#         pass
#
#     @position_m.setter
#     def position_m(self, pos_m):
#         self._position = pos_m
