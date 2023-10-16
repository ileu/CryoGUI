from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QApplication


class testing(QWidget):
    def __init__(self):
        super().__init__(
            parent=None,
        )

        self.button1 = QPushButton("Button 1")
        self.button2 = QPushButton("Button 2")

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        self.setLayout(self.layout)

        self.button1.clicked.connect(self.button1_clicked)
        self.button2.clicked.connect(self.button2_clicked)

        self.button1.setShortcut(Qt.Key.Key_X)
        self.button2.setShortcut(Qt.Key.Key_Y)

        self.button1.setEnabled(False)

    def button1_clicked(self):
        print("Button 1 clicked")

    def button2_clicked(self):
        print("Button 2 clicked")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q:
            self.button1_clicked()

        if event.key() == Qt.Key.Key_W:
            self.button2_clicked()


if __name__ == "__main__":
    app = QApplication([])

    widget = testing()
    widget.show()

    app.exec()
