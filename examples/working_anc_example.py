import time

import pymeasure
from pymeasure.instruments.attocube import ANC300Controller

print(pymeasure.__version__)

# to use the ANC300Controller, you need to to change the flush buffer operation to recieve buffer
axis_names = ["RZ", "RY", "RX", "LZ", "LY", "LX"]
controller = ANC300Controller(
    adapter="TCPIP::192.168.1.2::7230::SOCKET",
    axisnames=axis_names,
    passwd="123456",
)

for axis in axis_names:
    ax = getattr(controller, axis)
    print(ax.frequency)

controller.LX.mode = "stp"
controller.LX.stepu = 1
time.sleep(0.05)
controller.LX.stepd = 1

print(controller.version)
controller.ground_all()
