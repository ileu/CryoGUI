from typing import List

from PyQt5 import QtCore
from pyqtgraph import PlotWidget, mkPen

# def plot_data(self, new_data_points):
#     for data, data_point, plot_widget in zip(
#         self.data, new_data_points, self.plot_widgets
#     ):
#         print(data_point)
#         data.append(data_point)
#         if len(data) > 200:
#             data = data[-200:]
#         plot_widget.plot(data, clear=True, pen=pg.mkPen("b"))  # Blue pen
#         if len(data) > 1:
#             plot_widget.enableAutoRange("x")


class PlotWorker(QtCore.QObject):
    updatedValue = QtCore.pyqtSignal(float)

    def __init__(self, plot_widgets: List[PlotWidget], parent, data_names, data_units):
        """

        :param plot_widget:
        :param parent:
        """
        super().__init__()

        self.plot_widgets = plot_widgets
        self.parent = parent
        self.data = []
        self.data_names = data_names
        self.data_units = data_units

        self._ymin = -1
        self._ymax = 1

        for i, plot_widget in enumerate(self.plot_widgets):
            self.data.append([])
            plot_widget.showGrid(x=True, y=True, alpha=0.1)
            # plot_widget.getAxis("bottom").setLabel("Time", units="s")
            plot_widget.getAxis("left").setLabel(
                self.data_names[i] + f" / {self.data_units[i]}"
            )
            plot_widget.getAxis("bottom").setPen(mkPen(color="k"))
            plot_widget.getAxis("left").setPen(mkPen(color="k"))
            plot_widget.showAxis("right")
            plot_widget.getAxis("right").setStyle(showValues=False)
            plot_widget.getAxis("right").setPen(mkPen(color="k"))
            plot_widget.showAxis("top")
            plot_widget.getAxis("top").setStyle(showValues=False)
            plot_widget.getAxis("top").setPen(mkPen(color="k"))
            plot_widget.setBackground("w")  # White background
            plot_widget.getPlotItem().setContentsMargins(0, 0, 25, 10)
            # plot_widget.setStyleSheet(
            #     "border: 0px solid gray; border-radius: 5px; padding: 2px; background-color: white"
            # )
            plot_widget.setStyleSheet("background-color: white")
            if i != 0:
                plot_widget.setXLink(self.plot_widgets[0])

    @QtCore.pyqtSlot(list)
    def update(self, y_datas):
        for i, data, plot_widget in zip(range(5), y_datas, self.plot_widgets):
            self.data[i].append(data)
            plot_widget.plot(self.data[i], clear=True, pen=mkPen("b"))

            if self.data_names[i] == "Power":
                if data <= 1e-4:
                    plot_widget.ax.set_title(
                        str(int(data[-1] * 100 * 1e6) / 100) + " pW"
                    )
                elif data <= 1e-1:
                    plot_widget.set_title(str(int(data[-1] * 100 * 1e3) / 100) + " nW")
                elif data <= 1e2:
                    plot_widget.set_title(str(int(data[-1] * 100) / 100) + " uW")
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
