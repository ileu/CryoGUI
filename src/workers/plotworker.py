from PyQt5 import QtCore
from pyqtgraph import PlotWidget


class PlotWorker(QtCore.QObject):
    updatedPower = QtCore.pyqtSignal(float)

    def __init__(self, plot_widget, parent):
        super(PlotWorker, self).__init__()

        self.wdg: PlotWidget = plot_widget
        self.parent = parent

        self._ymin = -1
        self._ymax = 1

    @QtCore.pyqtSlot(object, object)
    def update(self, x_data, y_data):
        if not self.wdg.canvas.line:
            self.wdg.canvas.line = self.wdg.canvas.ax.plot(x_data, y_data)
            self.wdg.canvas.line = self.wdg.canvas.line[0]
        else:
            self.wdg.canvas.line.set_xdata(x_data)
            self.wdg.canvas.line.set_ydata(y_data)
        if self.parent.autoScale.isChecked():
            self.rescale_y(y_data)

        if y_data[-1] <= 1e-4:
            self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100 * 1e6) / 100) + " pW")
        elif y_data[-1] <= 1e-1:
            self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100 * 1e3) / 100) + " nW")
        elif y_data[-1] <= 1e2:
            self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100) / 100) + " uW")
        else:
            self.wdg.canvas.ax.set_title(
                str(int(y_data[-1] * 100 * 1e-3) / 100) + " mW"
            )

        self.wdg.canvas.ax.set_xlabel("Time [s]")
        self.wdg.canvas.ax.set_ylabel("Power [uW]")
        self.wdg.canvas.ax.set_ylim(self._ymin, self._ymax)
        self.wdg.canvas.ax.set_xlim([x_data.min(), x_data.max()])
        self.wdg.canvas.draw_idle()
        self.updatedPower.emit(y_data[-1])

    @QtCore.pyqtSlot(object)
    def rescale_y(self, array):
        y_min = array.min()
        y_max = array.max()
        y_span = y_max - y_min
        if y_span <= 0:
            if y_min == 0:
                self._ymin, self._ymax = y_min - 0.1, y_min + 0.1
            else:
                self._ymin, self._ymax = (y_min - 0.3 * y_min, y_max + 0.3 * y_min)
        else:
            self._ymin, self._ymax = (y_min - 0.3 * y_span, y_max + 0.3 * y_span)
