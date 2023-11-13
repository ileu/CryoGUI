import os
import time

from PyQt5.QtCore import QObject


class LogWorker(QObject):
    def __init__(self, filename, parent):
        super().__init__()
        self.parent = parent
        self.filename = filename

    def update(self, new_data_points):
        print_header = not os.path.exists(self.filename)

        with open(
            self.filename,
            "a",
        ) as f:
            if print_header:
                f.write("time," + ",".join(self.data_titles) + "\n")
                f.flush()
            line = str(time.time())
            line += ",".join(map(str, new_data_points))
            f.write(line + "\n")
            f.flush()
