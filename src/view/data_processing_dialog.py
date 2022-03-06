from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget

from src.view.basic_data_check_widget import BasicDataCheckWidget
from src.view.corrected_data_widget import CorrectedDataWidget
from src.view.drift_correction_widget import DriftCorrectionWidget
from src.view.quality_control_widget import QualityControlWidget
from src.view.sample_tree import SampleTreeWidget


class DataProcessingDialog(QDialog):
    def __init__(self, model):
        QDialog.__init__(self)

        self.model = model
        self.samples = model.samples_by_name.values()
        self.sample_tree = SampleTreeWidget(self)

        self.method = model.method

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

        self.sample_tree.set_samples(self.samples)
        self.sample_tree.select_first_spot()

        layout.addWidget(self.sample_tree)
        return layout

    def _create_left_layout(self):
        self.tabs = QTabWidget()
        self.tabs.addTab(BasicDataCheckWidget(self), "1. Basic data check")
        self.tabs.addTab(DriftCorrectionWidget(self), "2. Drift correction")
        self.tabs.addTab(QualityControlWidget(self), "3. Quality control")
        self.tabs.addTab(CorrectedDataWidget(self), "4. Corrected data")

        layout = QVBoxLayout()

        layout.addWidget(self.tabs)

        return layout


