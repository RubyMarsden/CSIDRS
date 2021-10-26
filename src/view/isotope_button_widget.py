from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from src.model.isotopes import Isotope
from src.view.method_selection_dialog import MethodSelectionDialog
from src.controllers.signals import Signals


class IsotopeButtonWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)

        self.model = model

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
        if result:
            self.emit_methods_signal(dialog)
        return

    def on_S_button_pushed(self):
        isotope = Isotope.SUL
        dialog = MethodSelectionDialog(isotope)
        result = dialog.exec()
        if result:
            self.emit_methods_signal(dialog)
        return

    def emit_methods_signal(self, dialog):
        if dialog.isotopes and dialog.material is not None:
            print(dialog.isotopes)
            print(dialog.material)
            self.model.signals.isotopesInput.emit(dialog.isotopes)
            self.model.signals.materialInput.emit(dialog.material)