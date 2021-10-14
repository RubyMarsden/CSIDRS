from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel


class FileEntryWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel("File entry goes here")

        layout.addWidget(label)
