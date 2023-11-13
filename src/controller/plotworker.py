from typing import List

from PyQt5 import QtCore
from pyqtgraph import PlotWidget, mkPen


class PlotWorker(QtCore.QObject):
    updatedValue = QtCore.pyqtSignal(float)

    def __init__(self, plot_widgets: List[PlotWidget], parent):
        """

        :param plot_widget:
        :param parent:
        """
        super().__init__()

        self.plot_widgets = plot_widgets
        self.parent = parent
        self.data = [[] for i in range(5)]

        self._ymin = -1
        self._ymax = 1

    @QtCore.pyqtSlot(list)
    def update(self, y_datas):
        for i, data, plot_widget in zip(range(5), y_datas, self.plot_widgets):
            print(i, data)
            self.data[i].append(data)
            plot_widget.plot(self.data[i], clear=True, pen=mkPen("b"))
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
