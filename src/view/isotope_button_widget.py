from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from src.model.isotopes import Isotope
from src.view.method_selection_dialog import MethodSelectionDialog


class IsotopeButtonWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.create_O_button())
        layout.addWidget(self.create_S_button())

    def create_O_button(self):
        self.o_button = QPushButton("O")
        self.o_button.resize(100, 100)
        self.o_button.clicked.connect(self.on_O_button_pushed)
        return self.o_button

    def create_S_button(self):
        self.s_button = QPushButton("S")
        self.s_button.clicked.connect(self.on_S_button_pushed)
        return self.s_button

    def on_O_button_pushed(self):
        isotope = Isotope.OXY
        dialog = MethodSelectionDialog(isotope)
        result = dialog.exec()
        return

    def on_S_button_pushed(self):
        isotope = Isotope.SUL
        dialog = MethodSelectionDialog(isotope)
        result = dialog.exec()
        return
