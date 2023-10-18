import time

from onglabsuite.instruments.thorlabs.pm100d import PM100D
from pymeasure.instruments.attocube import ANC300Controller

import logging

logger = logging.getLogger(__name__)


def measure(devices, **kwargs):
    """

    :param devices:
    :param kwargs:
    :return:
    """
    logger.info("Starting step size measurement")

    # check if necessary devices are available
    if not devices["anc300"]:
        raise RuntimeError("No ANC300 device found")
    # if not devices["pm"]:
    #     raise RuntimeError("No powermeter device found")

    # get devices
    logger.info("Getting devices")

    anc300: ANC300Controller = devices["anc300"]
    pm: PM100D = devices["pm"]

    # parameters

    starting_voltage = 25  # volt
    delta_voltage = -1  # volt
    end_voltage = 15
    max_steps = 100

    save_path = "C:\\Users\\ONG_C62_01\\Documents\\test.csv"

    logger.info("Setting up devices")
    # setup devices
    anc300.stop_all()
    anc300.ground_all()

    anc300.LX.mode = "stp"

    # setup
    logger.info("Starting loop")
    for voltage in range(
        starting_voltage,
        end_voltage,
        delta_voltage,
    ):
        logger.info(f"setting voltage to {voltage}")
        anc300.LX.voltage = voltage
        logger.info(f"waiting for 5 seconds")
        time.sleep(5)

        logger.info(f"measuring power")
        # power = pm.measure_power()
        # logger.info(f"power is {power}")
        # logger.info(f"writing to file")
        # with open(save_path, "a") as f:
        # f.write(f"{voltage},{power}\n")

    anc300.LX.stop()
    anc300.LX.mode = "gnd"


if __name__ == "__main__":
    controller = ANC300Controller(
        adapter="TCPIP::192.168.1.2::7230::SOCKET",
        axisnames=["RZ", "RY", "RX", "LZ", "LY", "LX"],
        passwd="123456",
    )
    test_devices = {"anc300": controller, "pm": None}
    measure(test_devices)
