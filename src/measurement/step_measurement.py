import datetime
import os
import time

import numpy as np
from PyQt6.QtCore import pyqtSignal, QObject, QThread
from onglabsuite.instruments.thorlabs.pm100d import PM100D
from pymeasure.instruments.attocube import ANC300Controller

import logging

from pymeasure.instruments.attocube.anc300 import Axis

logger = logging.getLogger(__name__)


class StepMeasurement(QObject):
    newDataPoint = pyqtSignal(float)
    measurementFinished = pyqtSignal(bool)

    def __init__(self, devices=None):
        super().__init__()
        self.devices = devices
        self.running = True

    def measure(self, devices=None, **kwargs):
        """

        :param devices:
        :param kwargs:
        :return:
        """
        if devices is None:
            devices = self.devices
            if devices is None:
                raise RuntimeError("No devices given")

        logger.info("Starting step size measurement")

        # check if necessary devices are available
        if not devices["anc300"]:
            raise RuntimeError("No ANC300 device found")
        if not devices["pm"]:
            raise RuntimeError("No powermeter device found")

        # get devices
        logger.info("Getting devices")

        anc300: ANC300Controller = devices["anc300"]
        pm: PM100D = devices["pm"]

        # parameters

        starting_voltage = 26  # volt
        delta_voltage = -1  # volt
        end_voltage = 16
        power_avg = 5

        powers = np.empty((power_avg, 1))

        save_path = (
            r"C:\Users\ONG_C54_01\Documents\MeasurementData\Ueli\StepMeasurement"
        )

        logger.info("Setting up devices")
        # setup devices
        anc300.stop_all()
        anc300.ground_all()

        axis: Axis = anc300.LX

        axis.mode = "stp"

        time.sleep(1)

        # setup
        logger.info("Starting loop")
        try:
            for frequency in range(
                190,
                200,
                20,
            ):
                voltage = 20
                rep = 0
                # for rep, voltage in enumerate([starting_voltage] * 10):
                if not self.running:
                    logger.info("Measurement stopped")
                    break
                logger.info(f"setting voltage to {voltage}")
                axis.voltage = voltage
                axis.frequency = frequency
                # anc300.read()
                logger.debug(f"waiting for 1 seconds")
                time.sleep(1)

                date = datetime.datetime.now().strftime("%Y%m%d")
                filename = (
                    save_path + rf"\{date}_voltage-{voltage}_frequency-{frequency}_.csv"
                )
                while os.path.exists(filename):
                    if filename.split("_")[-2].isdigit():
                        file_ext = int(filename.split("_")[-2]) + 1
                        filename = (
                            "_".join(filename.split("_")[:-2]) + f"_{file_ext}_.csv"
                        )
                    else:
                        filename = filename[:-4] + f"0_.csv"
                logger.info(f"filename is {filename}")

                storage = []
                peak = False
                i = 0
                direction = 1

                logger.info("Stepping")
                while i < 300 or peak or direction == -1:
                    if not self.running:
                        logger.info("Stepping stopped")
                        break
                    if direction == 1:
                        axis.stepu = 1
                    else:
                        axis.stepd = 1
                    logger.debug(f"waiting for {2.0 / frequency} seconds")
                    time.sleep(0.1)
                    i += 1
                    if direction == 1:
                        logger.debug(f"measuring power")
                        for n in range(power_avg):
                            try:
                                powers[n] = pm.power_W
                                time.sleep(0.1)
                            except Exception as e:
                                logger.error(f"Error: {e}")
                                powers[n] = np.nan
                    else:
                        powers = np.array([pm.power_W] * power_avg)
                        logger.debug("Backwards power measurement")
                    power = np.nanmean(powers)
                    logger.debug(f"power is {power}")

                    storage.append(power)

                    if len(storage) > 5:
                        delta = np.sum(np.diff(storage[-5:]))
                        tot_storage = np.sum(storage[-5:])
                        logger.debug(f"delta is {delta}")
                        if delta < 0 and tot_storage > 1e-7:
                            logger.debug(f"peak detected")
                            peak = True

                    if direction == 1:
                        logger.debug(f"writing to file")

                        self.newDataPoint.emit(power)
                        with open(
                            filename,
                            "a",
                        ) as f:
                            f.write(f"{i}, step, {power}, watt, {peak}\n")
                            f.flush()

                    if peak and power < 1e-8:
                        # logger.info("stepped over peak")
                        # break
                        if direction == 1:
                            logger.info("stepping back")
                            direction = -1
                            peak = False
                            storage = []
                            i = 0
                        else:
                            logger.info("finished")
                            break
                # logger.info(f"stepping back {i} steps")
                # axis.stepd = i
                # time.sleep(i / axis.frequency * 1.2)
                # input("Press enter to continue")

        except Exception as e:
            print(f"Something went wrong: {e}")
        finally:
            logger.info("Disconnecting anc")
            axis.stop()
            axis.mode = "gnd"
            logger.info("Disconnecting powermeter")
            pm.close()
            time.sleep(1)
            logger.info("Measurement finished")
            self.measurementFinished.emit(True)


if __name__ == "__main__":
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    logger.info("Connecting devices")
    controller = ANC300Controller(
        adapter="TCPIP::192.168.1.2::7230::SOCKET",
        axisnames=["RZ", "RY", "RX", "LZ", "LY", "LX"],
        passwd="123456",
    )
    logger.info("ANC300 connected")
    powermeter = PM100D("USB0::0x1313::0x8078::P0021350::INSTR")
    logger.info("Powermeter connected")
    test_devices = {"anc300": controller, "pm": powermeter}
    logger.info("Calling measure")
    experiment = StepMeasurement()
    experiment.measure(test_devices)
