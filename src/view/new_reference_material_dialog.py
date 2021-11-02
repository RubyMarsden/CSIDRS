from PyQt5.QtWidgets import QDialog


class NewReferenceMaterialDialog(QDialog):
    def __init__(self, element):
        QDialog.__init__(self)
        self.element = element
        self.setWindowTitle("Add new reference material")
        self.setMinimumWidth(450)

    def add_reference_material(self):
        return
