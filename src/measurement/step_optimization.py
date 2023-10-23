import time

import numpy as np
from PyQt6.QtCore import pyqtSignal, QObject
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

        coarse_voltage = 22  # volt
        fine_voltage = 20  # volt
        slope_stepping = 10
        max_steps = 50
        power_avg = 5

        powers = np.empty((power_avg, 1))

        save_path = (
            r"C:\Users\ONG_C54_01\Documents\MeasurementData\Ueli\StepOptimization"
        )

        logger.info("Setting up devices")
        # setup devices
        anc300.stop_all()
        anc300.ground_all()

        axis: Axis = anc300.LX

        axis.mode = "stp+"

        time.sleep(1)

        # setup
        logger.info("Starting loop")
        try:
            powers = []
            # look if there is a slope
            logger.debug("Looking for slope")
            for i in range(slope_stepping):
                axis.stepu = 1
                time.sleep(0.1)
                try:
                    powers.append(pm.power_W)
                except Exception as e:
                    logger.warning(f"Error reading powermeter: {e}")
                    i -= 1

            check_slope_pos = np.all(np.diff(powers) > 0)
            check_slope_neg = np.all(np.diff(powers) < 0)

            if check_slope_pos:
                logger.info("Found positive slope")
                slope = 1
            elif check_slope_neg:
                logger.info("Found negative slope")
                slope = -1
            else:
                logger.info("No slope found")
        except Exception as e:
            logger.warning(f"Error optimizing axis: {e}")
        finally:
            logger.info("Disconnecting anc")
            axis.stop()
            axis.mode = "gnd"
            logger.info("Disconnecting powermeter")
            pm.close()
            time.sleep(1)
            logger.info("Measurement finished")
            self.measurementFinished.emit(True)
