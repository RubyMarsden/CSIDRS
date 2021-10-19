# Popup for reference selection
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QCheckBox, QPushButton
from src.model.settings.isotope_reference_materials import *
from src.view.new_reference_material_dialog import NewReferenceMaterialDialog


class ReferenceMaterialSelectionDialog(QDialog):
    def __init__(self, isotope):
        QDialog.__init__(self)
        self.isotope = isotope
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

        if self.isotope == "o":
            reference_materials = [*oxygen_reference_material_dict]

        elif self.isotope == "s":
            reference_materials = [*sulphur_reference_material_dict]

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
        # TODO: make isotope come from the model
        isotope = "s"
        dialog = NewReferenceMaterialDialog(isotope)
        result = dialog.exec()
        if result == QDialog.Accepted:
            return dialog.add_reference_material()
        return None

