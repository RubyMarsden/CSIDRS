# Popup for reference selection
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QCheckBox
from src.model.settings.isotope_reference_materials import *


class ReferenceMaterialSelectionDialog(QDialog):
    def __init__(self, isotope):
        QDialog.__init__(self)
        self.isotope = isotope
        self.setWindowTitle("Reference material selection")
        self.setMinimumWidth(450)
        layout = QVBoxLayout()

        title = QLabel("Select a primary reference material")

        self.reference_list = QVBoxLayout()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if self.isotope == "o":
            reference_materials = [*oxygen_reference_material_dict]

        elif self.isotope == "s":
            reference_materials = [*sulphur_reference_material_dict]

        else:
            raise Exception

        for i in range(0, len(reference_materials)):
            box = QCheckBox(reference_materials[i])
            self.reference_list.addWidget(box)

        layout.addWidget(title)
        layout.addLayout(self.reference_list)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


