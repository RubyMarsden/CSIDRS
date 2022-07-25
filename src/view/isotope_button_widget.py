from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton

from model.elements import Element
from view.method_selection_dialog import MethodSelectionDialog


class IsotopeButtonWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)

        self.model = model
        self.element = None

        layout = QHBoxLayout()

        for element in Element:
            layout.addWidget(self.create_element_button(element))

        self.setLayout(layout)

    def create_element_button(self, element):
        button = QPushButton(element.element_symbol)
        button.element = element
        button.clicked.connect(lambda x: self.on_element_button_pushed(button.element))

        return button

    def on_element_button_pushed(self, element):
        self.element = element
        dialog = MethodSelectionDialog(self.element)
        result = dialog.exec()
        if result:
            self.emit_methods_signal(dialog)

    def emit_methods_signal(self, dialog):
        if dialog.isotopes and dialog.material is not None:
            self.model.signals.isotopesInput.emit(dialog.isotopes, self.element)
            self.model.signals.materialInput.emit(dialog.material)
