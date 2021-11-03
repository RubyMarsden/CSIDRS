from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox


class ChangeSampleNamesDialog(QDialog):
    def __init__(self, sample_names):
        QDialog.__init__(self)

        self.setWindowTitle("Change sample names")
        self.setMinimumWidth(450)
        self.input_box_list = []
        self.sample_names = []

        layout = QVBoxLayout()

        for sample_name in sample_names:
            input_box = QLineEdit(sample_name)
            input_box.textChanged.connect(self.on_input_box_text_changed)
            self.input_box_list.append(input_box)

            layout.addWidget(input_box)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def on_input_box_text_changed(self):
        for input_box in self.input_box_list:
            self.sample_names.append(input_box.text())
