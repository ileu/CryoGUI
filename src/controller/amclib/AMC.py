from src.controller.amclib import ACS
from src.controller.amclib.about import About
from src.controller.amclib.access import Access
from src.controller.amclib.amcids import Amcids
from src.controller.amclib.control import Control
from src.controller.amclib.description import Description
from src.controller.amclib.diagnostic import Diagnostic
from src.controller.amclib.functions import Functions
from src.controller.amclib.move import Move
from src.controller.amclib.network import Network
from src.controller.amclib.res import Res
from src.controller.amclib.rotcomp import Rotcomp
from src.controller.amclib.rtin import Rtin
from src.controller.amclib.rtout import Rtout
from src.controller.amclib.status import Status
from src.controller.amclib.system_service import System_service
from src.controller.amclib.update import Update


class Device(ACS.Device):

    def __init__(self, address):
        super().__init__(address)

        self.about = About(self)
        self.access = Access(self)
        self.amcids = Amcids(self)
        self.control = Control(self)
        self.description = Description(self)
        self.diagnostic = Diagnostic(self)
        self.functions = Functions(self)
        self.move = Move(self)
        self.network = Network(self)
        self.res = Res(self)
        self.rotcomp = Rotcomp(self)
        self.rtin = Rtin(self)
        self.rtout = Rtout(self)
        self.status = Status(self)
        self.system_service = System_service(self)
        self.update = Update(self)


def discover():
    return Device.discover("amc")
