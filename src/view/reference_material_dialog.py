from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QRadioButton, \
    QGridLayout, QWidget, QFrame

from model.settings.isotope_reference_materials import reference_material_dictionary


class ReferenceMaterialSelectionDialog(QDialog):
    def __init__(self, model):
        QDialog.__init__(self)
        self.model = model
        self.element = model.element
        self.material = model.material
        self.signals = model.signals
        self.primary_reference_material_selection = None
        self.secondary_reference_material_selection = None
        self.primary_radiobuttons = []
        self.secondary_radiobuttons = []
        self.setWindowTitle("Reference material selection")
        self.setMinimumWidth(450)
        layout = QGridLayout()

        title = QLabel("Select a primary reference material")
        secondary_title = QLabel("Select a secondary reference material")

        self.reference_list_widget = QWidget()
        self.secondary_reference_list_widget = QWidget()

        self.line = QFrame()
        self.line.setFrameShape(QFrame.VLine)
        self.line.setLineWidth(1)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        reference_materials = []
        for (i, j, k) in reference_material_dictionary.keys():
            if i == self.element and j == self.material:
                reference_materials.append(k)

        layout_one = QVBoxLayout()
        layout_two = QVBoxLayout()
        for i in range(0, len(reference_materials)):
            box1 = QRadioButton(reference_materials[i])
            box2 = QRadioButton(reference_materials[i])
            box1.reference_material = reference_materials[i]
            box2.reference_material = reference_materials[i]

            self.primary_radiobuttons.append(box1)
            self.secondary_radiobuttons.append(box2)

            box1.toggled.connect(self.on_primary_radio_button_selected)
            box2.toggled.connect(self.on_secondary_radio_button_selected)

            layout_one.addWidget(box1)
            layout_two.addWidget(box2)

        self.no_secondary_box = QRadioButton("No secondary reference material")
        self.secondary_radiobuttons.append(self.no_secondary_box)
        self.no_secondary_box.toggled.connect(self.on_secondary_radio_button_selected)

        layout_two.addWidget(self.no_secondary_box)

        self.reference_list_widget.setLayout(layout_one)
        self.secondary_reference_list_widget.setLayout(layout_two)

        layout.addWidget(title, 0, 0)
        layout.addWidget(secondary_title, 0, 1)
        layout.addWidget(self.reference_list_widget, 1, 0)
        layout.addWidget(self.line)
        layout.addWidget(self.secondary_reference_list_widget, 1, 1)
        layout.addWidget(self.buttonBox, 2, 1)
        self.setLayout(layout)

    def get_selected_reference_material(self):
        self.model.set_reference_materials(self.primary_reference_material_selection,
                                           self.secondary_reference_material_selection)

    def on_primary_radio_button_selected(self):
        for box in self.primary_radiobuttons:
            if box.isChecked():
                self.primary_reference_material_selection = box.text()
                for box2 in self.secondary_radiobuttons:
                    if box.text() == box2.text():
                        box2.setEnabled(False)
                    else:
                        box2.setEnabled(True)

        if self.primary_reference_material_selection and self.secondary_reference_material_selection:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def on_secondary_radio_button_selected(self):
        for box in self.secondary_radiobuttons:
            if box.isChecked():
                self.secondary_reference_material_selection = box.text()
                for box2 in self.primary_radiobuttons:
                    if box.text() == box2.text():
                        box2.setEnabled(False)
                    else:
                        box2.setEnabled(True)

        if self.primary_reference_material_selection and self.secondary_reference_material_selection:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
