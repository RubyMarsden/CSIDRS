from PyQt5.QtWidgets import QDialog, QLayout, QVBoxLayout, QPushButton, QHBoxLayout

from src.view.cycle_data_dialog import CycleDataDialog


class DataProcessingDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Data processing")
        self.setMinimumWidth(450)

        right_layout = self._create_right_layout()
        left_layout = self._create_left_layout()

        layout = QHBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        self.setLayout(layout)

    def _create_right_layout(self):
        layout = QVBoxLayout()
        return layout

    def _create_left_layout(self):
        layout = QVBoxLayout()
        cycle_data_button = QPushButton("Operators only")
        cycle_data_button.clicked.connect(self.on_cycle_data_button_pushed)
        layout.addWidget(cycle_data_button)
        return layout

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog()
        result = dialog.exec()
