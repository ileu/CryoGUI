from PyQt5 import QtCore
from pyqtgraph import PlotWidget


class PlotWorker(QtCore.QObject):
    updatedValue = QtCore.pyqtSignal(float)

    def __init__(self, plot_widget: PlotWidget, parent):
        """

        :param plot_widget:
        :param parent:
        """
        super().__init__()

        self.plot_widget = plot_widget
        self.parent = parent

        self._ymin = -1
        self._ymax = 1

    @QtCore.pyqtSlot(object, object)
    def update(self, x_data, y_data):
        self.plot_widget.plot(x_data, y_data)
        # if self.parent.autoScale.isChecked():
        #     self.rescale_y(y_data)
        #
        # if y_data[-1] <= 1e-4:
        #     self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100 * 1e6) / 100) + " pW")
        # elif y_data[-1] <= 1e-1:
        #     self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100 * 1e3) / 100) + " nW")
        # elif y_data[-1] <= 1e2:
        #     self.wdg.canvas.ax.set_title(str(int(y_data[-1] * 100) / 100) + " uW")
        # else:
        #     self.wdg.canvas.ax.set_title(
        #         str(int(y_data[-1] * 100 * 1e-3) / 100) + " mW"
        #     )
        #
        # self.wdg.canvas.ax.set_xlabel("Time [s]")
        # self.wdg.canvas.ax.set_ylabel("Power [uW]")
        # self.wdg.canvas.ax.set_ylim(self._ymin, self._ymax)
        # self.wdg.canvas.ax.set_xlim([x_data.min(), x_data.max()])
        # self.wdg.canvas.draw_idle()
        # self.updatedValue.emit(y_data[-1])
