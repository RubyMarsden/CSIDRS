# Dialog for selecting isotopes and material type for method
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QVBoxLayout, QCheckBox, QWidget, QDialogButtonBox, \
    QRadioButton

from src.model.isotopes import Isotope
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

        self.isotope_box_list = []
        self.material_box_list = []

        self.isotopes = []
        self.material = None

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        lhs_box_layout = QVBoxLayout()
        rhs_box_layout = QVBoxLayout()

        if self.isotope == Isotope.OXY:

            for isotope in oxygen_isotope_list:
                box = QCheckBox(isotope)
                box.isotope = isotope
                box.stateChanged.connect(self.on_isotopes_changed)

                lhs_box_layout.addWidget(box)
                self.isotope_box_list.append(box)

            for material in oxygen_material_list:
                box = QRadioButton(material)
                box.material = material
                box.toggled.connect(self.on_material_changed)

                rhs_box_layout.addWidget(box)
                self.material_box_list.append(box)

        elif self.isotope == Isotope.SUL:

            for isotope in sulphur_isotope_list:
                box = QCheckBox(isotope)
                box.isotope = isotope
                box.stateChanged.connect(self.on_isotopes_changed)

                lhs_box_layout.addWidget(box)
                self.isotope_box_list.append(box)

            for material in sulphur_material_list:
                box = QRadioButton(material)
                box.material = material
                box.toggled.connect(self.on_material_changed)

                rhs_box_layout.addWidget(box)
                self.material_box_list.append(box)

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

    def on_isotopes_changed(self):
        self.isotopes.clear()
        for box in self.isotope_box_list:
            if box.isChecked():
                self.isotopes.append(box.isotope)

    def on_material_changed(self):
        self.material = None
        for box in self.material_box_list:
            if box.isChecked():
                self.material = box.material




