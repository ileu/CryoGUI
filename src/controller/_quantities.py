import abc
import numpy as np


class PowerQty(object, metaclass=abc.ABCMeta):
    """Abstract base-class for power unit conversions."""
    @property
    def power(self):
        raise AttributeError("Use power_units, eg. power_uW")

    @property
    @abc.abstractmethod
    def power_W(self):
        pass

    @power_W.setter
    @abc.abstractmethod
    def power_W(self, pow_W):
        pass

    @property
    def power_mW(self):
        return self.power_W * 1e3

    @power_mW.setter
    def power_mW(self, pow_mW):
        self.power_W = pow_mW * 1e-3

    @property
    def power_uW(self):
        return self.power_W * 1e6

    @power_uW.setter
    def power_uW(self, pow_uW):
        self.power_W = pow_uW * 1e-6

    @property
    def power_nW(self):
        return self.power_W * 1e9

    @power_nW.setter
    def power_nW(self, pow_nW):
        self.power_W = pow_nW * 1e-9

    @property
    def power_dBm(self):
        return 10 * np.log10(self.power_mW)

    @power_dBm.setter
    def power_dBm(self, pow_dBm):
        self.power_W = 10 ** (pow_dBm / 10.) * 1e-3


class WavelengthQty(object, metaclass=abc.ABCMeta):
    """Abstract base-class for wavelength unit conversions."""
    @property
    def wavelength(self):
        raise AttributeError("Use wavelength_units, eg. wavelength_nm")

    @property
    @abc.abstractmethod
    def wavelength_m(self):
        pass

    @wavelength_m.setter
    @abc.abstractmethod
    def wavelength_m(self, wl_m):
        pass

    @property
    def wavelength_um(self):
        return self.wavelength_m * 1e6

    @wavelength_um.setter
    def wavelength_um(self, wl_um):
        self.wavelength_m = wl_um * 1e-6

    @property
    def wavelength_nm(self):
        return self.wavelength_m * 1e9

    @wavelength_nm.setter
    def wavelength_nm(self, wl_nm):
        self.wavelength_m = wl_nm * 1e-9


class PositionQty(object, metaclass=abc.ABCMeta):
    """Abstract base-class for wavelength unit conversions."""
    @property
    def position(self):
        raise AttributeError("Use wavelength_units, eg. wavelength_nm")

    @property
    @abc.abstractmethod
    def position_m(self):
        pass

    @position_m.setter
    @abc.abstractmethod
    def position_m(self, pos_m):
        pass

    @property
    def position_mm(self):
        return self.position_m * 1e3

    @position_mm.setter
    def position_mm(self, pos_mm):
        self.position_m = pos_mm * 1e-3

    @property
    def position_cm(self):
        return self.position_m * 1e2

    @position_cm.setter
    def position_cm(self, pos_cm):
        self.position_m = pos_cm * 1e-2

    @property
    def position_um(self):
        return self.position_m * 1e6

    @position_um.setter
    def position_um(self, pos_um):
        self.position_m = pos_um * 1e-6

    @property
    def position_nm(self):
        return self.position_m * 1e9

    @position_nm.setter
    def position_nm(self, pos_nm):
        self.position_m = pos_nm * 1e-9
