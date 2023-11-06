import os.path
import time

import numpy as np
from PyQt5.QtCore import pyqtSignal, QObject
from onglabsuite.instruments.thorlabs.pm100d import PM100D
from pymeasure.instruments.attocube import ANC300Controller

import logging

from pymeasure.instruments.attocube.anc300 import Axis

logger = logging.getLogger(__name__)
print(__name__)


class OptimizationMeasurement(QObject):
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

        coarse_voltage = 24  # volt
        fine_voltage = 20  # volt
        frequency = 100  # Hz
        slope_stepping = 10
        max_steps = 50
        power_avg = 5

        powers = []
        max_power = 0

        save_path = os.path.expanduser(
            r"~\Documents\MeasurementData\Ueli\StepOptimization"
        )

        logger.info("Setting up devices")
        # setup devices
        anc300.stop_all()
        anc300.ground_all()

        axis: Axis = anc300.LY

        axis.mode = "stp+"

        time.sleep(1)

        # setup
        logger.info("Starting loop")
        try:
            logger.debug("Looking for slope")
            axis.voltage = coarse_voltage
            axis.frequency = frequency
            for i in range(slope_stepping):
                axis.stepu = 1
                time.sleep(0.25)
                try:
                    if not pm.instrument.waiting:
                        powers.append(pm.power_uW)
                        self.newDataPoint.emit(powers[-1])
                except Exception as e:
                    logger.warning(f"Error reading powermeter: {e}")
                    i -= 2
                if i < 0:
                    raise RuntimeError("No powermeter reading")

            check_slope_pos = np.all(np.diff(powers) > 0)
            check_slope_neg = np.all(np.diff(powers) < 0)
            logger.info("Powers: " + str(powers))
            logger.info("Power diffs: " + str(np.diff(powers)))

            if check_slope_pos:
                logger.info("Found positive slope")
                slope = -1
            elif check_slope_neg:
                logger.info("Found negative slope")
                slope = 1
            else:
                logger.info("No slope found")
                raise RuntimeError("No slope found")

            time.sleep(2)
            # find peak
            logger.info("Finding peak")
            for voltage in [25, 22, 20, 18, 16]:
                powers = []
                axis.voltage = voltage
                axis.frequency = frequency

                time.sleep(0.1)

                logger.info(f"setting voltage to {voltage}")

                # step in reverse direction to slope
                for i in range(max_steps):
                    power = 0
                    logger.info(f"SLOPE: {slope}")
                    if slope == -1:
                        axis.stepu = 1
                    else:
                        axis.stepd = 1
                    logger.debug(f"waiting for {0.05} seconds")
                    time.sleep(0.1)
                    while power == 0:
                        try:
                            power = pm.power_W
                        except Exception as e:
                            logger.error(f"Error reading powermeter: {e}")
                            power = 0
                            time.sleep(0.1)
                    powers.append(power)
                    self.newDataPoint.emit(power)
                    if power > max_power:
                        max_power = power

                    # check if slope has changed
                    if len(powers) > 2:
                        check_slope = np.all(np.diff(powers[-5:]) < 0)
                    else:
                        check_slope = False

                    if check_slope:
                        logger.warning("Slope changed")
                        slope = -slope
                        break
                else:
                    logger.error("RAN OUT OF STEPS ")
                    break
            time.sleep(1)
            if slope == 1:
                axis.stepu = 3
            else:
                axis.stepd = 3
            logger.info("Found peak")
            print(max_power)
            peak_power = pm.power_W
            logger.info(f"Peak power: {peak_power}")
            self.newDataPoint.emit(peak_power)

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
