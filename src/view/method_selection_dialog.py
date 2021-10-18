# Dialog for selecting isotopes and material type for method
from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QVBoxLayout, QCheckBox, QWidget, QDialogButtonBox


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

        if self.isotope == "o":
            lhs_box_layout = QVBoxLayout()
            box1 = QCheckBox("16O")
            box2 = QCheckBox("18O")
            box3 = QCheckBox("OH")
            lhs_box_layout.addWidget(box1)
            lhs_box_layout.addWidget(box2)
            lhs_box_layout.addWidget(box3)
            self.lhs_box_list.setLayout(lhs_box_layout)

            rhs_box_layout = QVBoxLayout()
            box1 = QCheckBox("Zircon")
            box2 = QCheckBox("Zircon")
            box3 = QCheckBox("Zircon")
            rhs_box_layout.addWidget(box1)
            rhs_box_layout.addWidget(box2)
            rhs_box_layout.addWidget(box3)
            self.rhs_box_list.setLayout(rhs_box_layout)

        elif self.isotope == "s":
            lhs_box_layout = QVBoxLayout()
            box1 = QCheckBox("32S")
            box2 = QCheckBox("33S")
            box3 = QCheckBox("34S")
            box4 = QCheckBox("36S")
            lhs_box_layout.addWidget(box1)
            lhs_box_layout.addWidget(box2)
            lhs_box_layout.addWidget(box3)
            lhs_box_layout.addWidget(box4)
            self.lhs_box_list.setLayout(lhs_box_layout)

            rhs_box_layout = QVBoxLayout()
            box1 = QCheckBox("Zircon")
            box2 = QCheckBox("Zircon")
            box3 = QCheckBox("Zircon")
            rhs_box_layout.addWidget(box1)
            rhs_box_layout.addWidget(box2)
            rhs_box_layout.addWidget(box3)
            self.rhs_box_list.setLayout(rhs_box_layout)

        else:
            raise Exception

        layout.addWidget(lhs_title, 0, 0)
        layout.addWidget(self.lhs_box_list, 1, 0)
        layout.addWidget(rhs_title, 0, 1)
        layout.addWidget(self.rhs_box_list, 1, 1)
        layout.addWidget(self.buttonBox, 2, 1)

        self.setLayout(layout)
