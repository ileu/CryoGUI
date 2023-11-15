import os
import time

from PyQt5.QtCore import QObject, pyqtSignal


# def logging_manager(self, running: bool = False):
#     if running:
#         dialog = QFileDialog(self)
#         dialog.setDirectory(os.path.join(os.path.dirname(__file__)))
#         dialog.setFileMode(QFileDialog.FileMode.AnyFile)
#         dialog.setViewMode(QFileDialog.ViewMode.List)
#
#         date = datetime.datetime.now().strftime("%Y%m%d")
#
#         filename, filetype = dialog.getSaveFileName(
#             self,
#             "Save File",
#             f"{date}_log_file",
#             "Text Files (*.txt);; CSV (*.csv)",
#             )
#         self.action_monitor.append(f"Log file path: {filename}")
#         if filename:
#             self.file_locator.setText(filename)
#             if not os.path.exists(filename):
#                 with open(
#                         filename,
#                         "a",
#                         ) as f:
#                     f.write("time," + ",".join(self.data_titles) + "\n")
#                     f.flush()
#             self.log_file_browse.setText("Stop Logging")
#             self.log_file_location = filename
#             # self.logging_timer.start(1000)
#             # self.controller.updatedValues.connect(self.log_data)
#             self.file_locator.setEnabled(False)
#             self.logging_interval_edit.setEnabled(True)
#             self.action_monitor.append(f"Started logging to {filename}")
#         else:
#             self.log_file_browse.setChecked(False)
#     else:
#         self.log_file_browse.setText("Start Logging")
#
#         self.action_monitor.append(f"Logging stopped")
#         self.controller.updatedValues.disconnect(self.log_data)


class LogWorker(QObject):
    loggingFailed = pyqtSignal(str)

    def __init__(self, filename, parent, data_names):
        super().__init__()
        self.parent = parent
        self.filename = filename
        self.data_names = data_names
        self.remark = ""

    def set_filename(self, filename):
        self.filename = filename

    def set_remark(self, remark):
        self.remark = remark

    def update(self, new_data_points):
        print_header = not os.path.exists(self.filename)
        if not self.filename:
            self.loggingFailed.emit("No filename given")
            return

        with open(
            self.filename,
            "a",
        ) as f:
            if print_header:
                f.write("time," + ",".join(self.data_names) + f",remarks" "\n")
                f.flush()
            line = f"{time.time()},"
            line += ",".join(map(str, new_data_points))
            line += f",{self.remark}"
            f.write(line + "\n")
            f.flush()
