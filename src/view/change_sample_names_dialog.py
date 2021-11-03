from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox


class ChangeSampleNamesDialog(QDialog):
    def __init__(self, sample_names):
        QDialog.__init__(self)

        self.setWindowTitle("Change sample names")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        for sample_name in sample_names:
            input_box = QLineEdit(sample_name)

            layout.addWidget(input_box)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
