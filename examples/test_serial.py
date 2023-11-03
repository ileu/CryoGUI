from PyQt5 import QtCore, QtWidgets, QtSerialPort


class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.output_te = QtWidgets.QTextEdit()
        self.output_te.setReadOnly(True)

        self.button = QtWidgets.QPushButton(text="Connect")
        self.button.setCheckable(True)
        self.button.toggled.connect(self.on_toggled)

        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        lay.addLayout(hlay)
        lay.addWidget(self.output_te)
        lay.addWidget(self.button)

        self.ports = QtSerialPort.QSerialPortInfo.availablePorts()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        # self.serial = QtSerialPort.QSerialPort(self.ports[2])
        # self.serial.readyRead.connect(self.receive)

    def keyPressEvent(self, event):
        print("Press: ", event.key())

    def keyReleaseEvent(self, event):
        print("Release", event.key())

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip("\r\n")
            self.output_te.append(text)

    @QtCore.pyqtSlot()
    def send(self):
        self.serial.write(self.message_le.text().encode())

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial.isOpen():
                if not self.serial.open(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly):
                    self.button.setChecked(False)
        else:
            self.serial.close()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())
