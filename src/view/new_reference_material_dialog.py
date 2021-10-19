from PyQt5.QtWidgets import QDialog


class NewReferenceMaterialDialog(QDialog):
    def __init__(self, isotope):
        QDialog.__init__(self)
        self.isotope = isotope
        self.setWindowTitle("Add new reference material")
        self.setMinimumWidth(450)

    def add_reference_material(self):
        return
