from PyQt5.QtWidgets import QDialog, QLayout, QVBoxLayout, QPushButton, QHBoxLayout, QTreeWidget, QTabWidget

from src.view.basic_data_check_widget import BasicDataCheckWidget
from src.view.cycle_data_dialog import CycleDataDialog
from src.view.drift_correction_widget import DriftCorrectionWidget


class DataProcessingDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Data processing")
        self.setMinimumWidth(500)

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
        self.tabs = QTabWidget()
        self.tabs.addTab(BasicDataCheckWidget(self), "1. Basic data check")
        self.tabs.addTab(DriftCorrectionWidget(self), "2. Drift correction")

        layout = QVBoxLayout()

        layout.addWidget(self.tabs)

        return layout


