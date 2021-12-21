from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from src.model.elements import Element
from src.view.method_selection_dialog import MethodSelectionDialog


class IsotopeButtonWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)

        self.model = model
        self.element = None

        layout = QHBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.create_O_button())
        layout.addWidget(self.create_S_button())
        layout.addWidget(self.create_Cl_button())

    def create_O_button(self):
        o_button = QPushButton("O")
        o_button.clicked.connect(self.on_O_button_pushed)
        return o_button

    def create_S_button(self):
        s_button = QPushButton("S")
        s_button.clicked.connect(self.on_S_button_pushed)
        return s_button

    def create_Cl_button(self):
        cl_button = QPushButton("Cl")
        cl_button.clicked.connect(self.on_Cl_button_pushed)
        return cl_button

    def on_O_button_pushed(self):
        self.element = Element.OXY
        dialog = MethodSelectionDialog(self.element)
        result = dialog.exec()
        if result:
            self.emit_methods_signal(dialog)
    def on_S_button_pushed(self):
        self.element = Element.SUL
        dialog = MethodSelectionDialog(self.element)
        result = dialog.exec()
        if result:
            self.emit_methods_signal(dialog)
    def on_Cl_button_pushed(self):
        self.element = Element.CHL
        dialog = MethodSelectionDialog(self.element)
        result = dialog.exec()
        if result:
            self.emit_methods_signal(dialog)

    def emit_methods_signal(self, dialog):
        if dialog.isotopes and dialog.material is not None:
            self.model.signals.isotopesInput.emit(dialog.isotopes, self.element)
            self.model.signals.materialInput.emit(dialog.material.value)
