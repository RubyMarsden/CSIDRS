from PyQt5.QtWidgets import QDialog, QVBoxLayout, QDoubleSpinBox, QLineEdit


class ChangeSampleNamesDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Change sample names")
        self.setMinimumWidth(450)

        layout = QVBoxLayout()

        input_box = QLineEdit()

        layout.addWidget(input_box)

        self.setLayout(layout)
