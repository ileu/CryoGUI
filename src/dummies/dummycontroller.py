import logging

logger = logging.getLogger(__name__)


class DummyController:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __getattr__(self, item):
        logger.debug(f"get {item}")
        try:
            return super().__getattribute__(item)
        except AttributeError:
            return None

    def __setattr__(self, key, value):
        logger.debug(f"set {key}: {value}")
        super().__setattr__(key, value)


# class DummyAMC300Controller(AMC300Controller):
#     def __init__(self, ip):
#         super().__init__(ip)
#         self.ip = ip
#
#         self.axes: List[DummyOpenLoopAxis] = []
#
#         self._position = 0
#
#     def connect(self):
#         for i in range(3):
#             self.axes.append(DummyOpenLoopAxis(i))
#         return True
#
#     def disconnect(self):
#         return True


class DummyAttoDRY(DummyController):
    def __init__(self):
        super().__init__()
        self.started = False
        self.connected = False
        self.com_port = None

    def begin(self):
        self.started = True

    def end(self):
        self.started = False

    def Connect(self, com_port):
        self.connected = True
        self.com_port = com_port

    def Disconnect(self):
        self.connected = False
        self.com_port = None
