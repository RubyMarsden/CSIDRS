from PyQt5.QtWidgets import QDialog, QLayout, QVBoxLayout, QPushButton, QHBoxLayout, QTreeWidget, QTabWidget

from src.view.basic_data_check_widget import BasicDataCheckWidget
from src.view.corrected_data_widget import CorrectedDataWidget
from src.view.cycle_data_dialog import CycleDataDialog
from src.view.drift_correction_widget import DriftCorrectionWidget
from src.view.sample_tree import SampleTreeWidget


class DataProcessingDialog(QDialog):
    def __init__(self, samples, method_dictionary):
        QDialog.__init__(self)

        self.samples = samples
        self.sample_tree = SampleTreeWidget()

        self.method_dictionary = method_dictionary

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

        self.sample_tree.set_samples(self.samples)
        self.sample_tree.select_first_spot()

        next_button = QPushButton("Next")
        back_button = QPushButton("Back")

        button_layout.addWidget(back_button)
        button_layout.addWidget(next_button)

        layout.addWidget(self.sample_tree)
        layout.addLayout(button_layout)
        return layout

    def _create_left_layout(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(BasicDataCheckWidget(self), "1. Basic data check")
        self.tabs.addTab(DriftCorrectionWidget(self), "2. Drift correction")
        self.tabs.addTab(CorrectedDataWidget(self), "3. Corrected data")

        layout = QVBoxLayout()

        layout.addWidget(self.tabs)

        return layout


