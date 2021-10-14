from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton


class IsotopeButtonWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.create_O_button())
        layout.addWidget(self.create_S_button())

    def create_O_button(self):
        o_button = QPushButton("O")
        o_button.resize(100, 100)
        return o_button

    def create_S_button(self):
        s_button = QPushButton("S")
        return s_button
