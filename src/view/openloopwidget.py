from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QApplication, QVBoxLayout, QHBoxLayout, QStyle

from src.view.utilitywidgets import SetWidget, IncrementWidget


class OpenLoopWidget(QWidget):
    def __init__(
            self,
            parent: QWidget = None,
            title: str = "Quantity",
            symbols: int = 7,
            unit: str = "",
            **kwargs
    ):
        super().__init__(parent, **kwargs)
        self.value = 0.0

        self.title_label = QLabel(title)
        self.status_label = QLabel("Status: Disconnected")

        self.voltage_widget = SetWidget(title="Voltage", symbols=4, unit=" V")
        self.frequency_widget = SetWidget(title="Frequency", symbols=4, unit=" Hz")

        self.step_widget = IncrementWidget(title="Step")

        self.gnd_button = QPushButton("OFF")

        self.move_button = QPushButton()

        self.symbols = symbols
        self.unit = unit
        self.grounded = False
        self.movable = False

        self.initUI()

    def initUI(self):
        self.move_button.setCheckable(True)
        self.move_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.move_button.setFixedSize(30, 20)
        self.move_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 0px; "
            "border-radius: 5px; font-size: 16px;"
            "background-color: rgb(255,75,50);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:hover:checked {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        # self.move_button.clicked.connect(self.toggle_moveable)

        self.gnd_button.setCheckable(True)
        self.gnd_button.setStyleSheet(
            "QPushButton {border: 2px solid black; padding-bottom: 2px; "
            "border-radius: 5px; font-size: 16px; font-weight: bold;"
            "background-color: rgb(180,180,255);}"
            "QPushButton:hover {background-color: rgb(228,241,251); }"
            "QPushButton:hover:checked {background-color: rgb(228,241,251); }"
            "QPushButton:pressed {background-color: rgb(204,228,247); }"
            "QPushButton:checked {background-color: rgb(0,255,0); }"
            "QPushButton:disabled {background-color: rgb(200,200,200); }"
        )
        self.gnd_button.setFixedSize(40, 20)
        # self.gnd_button.clicked.connect(self.toggle_gnd)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)

        text_layout = QHBoxLayout()
        text_layout.setSpacing(3)
        text_layout.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignLeft)
        text_layout.addStretch()
        text_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignRight)
        text_layout.addWidget(self.move_button, alignment=Qt.AlignmentFlag.AlignRight)
        text_layout.addWidget(self.gnd_button,  alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(text_layout)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(0)
        control_layout.addWidget(self.voltage_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        control_layout.addWidget(self.frequency_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        control_layout.addWidget(self.step_widget, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(control_layout)

        main_layout.addStretch()

        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication([])
    widget = OpenLoopWidget()
    widget.show()
    app.exec()
