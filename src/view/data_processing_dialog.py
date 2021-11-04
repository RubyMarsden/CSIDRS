from PyQt5.QtWidgets import QDialog, QLayout, QVBoxLayout, QPushButton, QHBoxLayout, QTreeWidget

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
        button_layout = QHBoxLayout()
        #TODO deal with the sample tree
        sample_tree = QTreeWidget()

        next_button = QPushButton("Next")
        back_button = QPushButton("Back")

        button_layout.addWidget(back_button)
        button_layout.addWidget(next_button)

        layout.addWidget(sample_tree)
        layout.addLayout(button_layout)
        return layout

    def _create_left_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        cycle_data_button = QPushButton("Operators only")
        cycle_data_button.clicked.connect(self.on_cycle_data_button_pushed)
        button_layout.addWidget(cycle_data_button)

        data_output_button = QPushButton("Extract data")
        data_output_button.clicked.connect(self.on_data_output_button_pushed)
        button_layout.addWidget(data_output_button)

        layout.addLayout(button_layout)
        return layout

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog()
        result = dialog.exec()

    def on_data_output_button_pushed(self):
        print("Create a csv")
        return
