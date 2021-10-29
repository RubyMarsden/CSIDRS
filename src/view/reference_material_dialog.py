# Popup for reference selection
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QCheckBox, QPushButton

from src.model.elements import Element
from src.model.settings.isotope_reference_materials import *
from src.view.new_reference_material_dialog import NewReferenceMaterialDialog


class ReferenceMaterialSelectionDialog(QDialog):
    def __init__(self, element, material):
        QDialog.__init__(self)
        self.element = element
        self.material = material
        self.setWindowTitle("Reference material selection")
        self.setMinimumWidth(450)
        layout = QVBoxLayout()

        title = QLabel("Select a primary reference material")

        self.reference_list = QVBoxLayout()
        self.new_reference_material_button = QPushButton("New reference")
        self.new_reference_material_button.setFixedWidth(150)
        self.new_reference_material_button.clicked.connect(self.new_reference_material_button_clicked)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        if self.element == Element.OXY:
            if self.material == "Zircon":
                reference_materials = [*oxygen_zircon_reference_material_dict]
            elif self.material == "Quartz":
                # TODO make quartz reference material dictionary
                reference_materials = []
            else:
                raise Exception

        elif self.element == Element.SUL:
            if self.material == "Pyrite":
                reference_materials = [*sulphur_pyrite_reference_material_dict]

        else:
            raise Exception

        for i in range(0, len(reference_materials)):
            box = QCheckBox(reference_materials[i])
            self.reference_list.addWidget(box)

        self.reference_list.addWidget(self.new_reference_material_button)

        layout.addWidget(title)
        layout.addLayout(self.reference_list)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    def get_selected_reference_material(self):
        # TODO: Add functionality
        return

    def new_reference_material_button_clicked(self):
        # TODO: make element come from the model
        element = self.element
        dialog = NewReferenceMaterialDialog(element)
        result = dialog.exec()
        if result == QDialog.Accepted:
            return dialog.add_reference_material()
        return None

