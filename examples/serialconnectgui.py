from PyQt5 import QtSerialPort, QtCore
from PyQt5.QtWidgets import (
    QDialog,
    QTextEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
)


class SerialConnect(QDialog):
    def __init__(self, parent=None):
        super(SerialConnect, self).__init__(parent)
        self.output_te = QTextEdit()
        self.output_te.setReadOnly(True)

        self.button = QPushButton(text="Connect")
        self.button.setCheckable(True)
        self.button.toggled.connect(self.on_toggled)

        self.port_combo = QComboBox()

        lay = QVBoxLayout(self)
        hlay = QHBoxLayout()
        lay.addLayout(hlay)
        lay.addWidget(self.output_te)
        lay.addWidget(self.button)

        self.ports = []
        self.serial = None
        self.init_serial_ports()

    def init_serial_ports(self):
        self.ports = QtSerialPort.QSerialPortInfo.availablePorts()
        for port in self.ports:
            self.port_combo.addItem(port.portName())

    @QtCore.pyqtSlot()
    def receive(self):
        while self.serial.canReadLine():
            text = self.serial.readLine().data().decode()
            text = text.rstrip("\r\n")
            self.output_te.append(text)

    # @QtCore.pyqtSlot(bool)
    # def on_toggled(self, checked):
    #     self.button.setText("Disconnect" if checked else "Connect")
    #     if checked:
    #         if not self.serial.isOpen():
    #             if not self.serial.open(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly):
    #                 self.button.setChecked(False)
    #     else:
    #         self.serial.close()

    @QtCore.pyqtSlot(bool)
    def on_toggled(self, checked):
        self.button.setText("Disconnect" if checked else "Connect")
        if checked:
            if not self.serial:
                self.init_serial_port()

            if self.serial:
                if not self.serial.isOpen():
                    if not self.serial.open(QtCore.QIODeviceBase.OpenModeFlag.ReadOnly):
                        self.button.setChecked(False)
                else:
                    pass
                # Connection successful, do any other initialization here
            else:
                # Handle the case where there are no available ports
                self.button.setChecked(False)
        else:
            if self.serial and self.serial.isOpen():
                self.serial.close()

    def init_serial_port(self):
        selected_port = self.port_combo.currentText()
        for port_info in self.ports:
            if port_info.portName() == selected_port:
                self.serial = QtSerialPort.QSerialPort(port_info)
                self.serial.readyRead.connect(self.receive)
                break

    def closeEvent(self, a0):
        if self.serial and self.serial.isOpen():
            self.serial.close()


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = SerialConnect()
    window.show()
    sys.exit(app.exec())
