# Dialog for selecting isotopes and material type for method
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QVBoxLayout, QCheckBox, QWidget, QDialogButtonBox, \
    QRadioButton

from src.model.settings.isotope_lists import *
from src.model.settings.material_lists import *

class MethodSelectionDialog(QDialog):
    def __init__(self, isotope):
        QDialog.__init__(self)
        self.isotope = isotope
        self.setWindowTitle("Isotope and material selection")
        self.setMinimumWidth(450)
        layout = QGridLayout()
        lhs_title = QLabel("Isotope")
        rhs_title = QLabel("Material")
        self.lhs_box_list = QWidget()
        self.rhs_box_list = QWidget()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        lhs_box_layout = QVBoxLayout()
        rhs_box_layout = QVBoxLayout()

        if self.isotope == "o":

            for isotope in oxygen_isotope_list:
                box = QCheckBox(isotope)
                lhs_box_layout.addWidget(box)

            for material in oxygen_material_list:
                box = QRadioButton(material)
                rhs_box_layout.addWidget(box)

        elif self.isotope == "s":

            for isotope in sulphur_isotope_list:
                box = QCheckBox(isotope)
                lhs_box_layout.addWidget(box)

            for material in sulphur_material_list:
                box = QRadioButton(material)
                rhs_box_layout.addWidget(box)

        else:
            raise Exception

        self.lhs_box_list.setLayout(lhs_box_layout)
        self.rhs_box_list.setLayout(rhs_box_layout)

        layout.addWidget(lhs_title, 0, 0)
        layout.addWidget(self.lhs_box_list, 1, 0)
        layout.addWidget(rhs_title, 0, 1)
        layout.addWidget(self.rhs_box_list, 1, 1)
        layout.addWidget(self.buttonBox, 2, 1)

        self.setLayout(layout)
