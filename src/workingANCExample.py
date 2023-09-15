import pymeasure
from pymeasure.instruments.attocube import ANC300Controller

print(pymeasure.__version__)

# to use the ANC300Controller, you need to to change the flush buffer operation to recieve buffer

controller = ANC300Controller(adapter="TCPIP::192.168.1.2::7230::SOCKET", axisnames=["RZ", "RY", "RX", "LZ", "LY", "LX"], passwd="123456")

print(controller.version)
controller.ground_all()
