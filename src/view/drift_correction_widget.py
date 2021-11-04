from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        layout = QHBoxLayout()

        lhs_layout = self._create_lhs_layout()
        rhs_layout = self._create_rhs_layout()

        layout.addLayout(lhs_layout)
        layout.addLayout(rhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        standard_table = QTableWidget()
        layout.addWidget(standard_table)

        return layout

    def _create_rhs_layout(self):
        layout = QVBoxLayout()

        graph_primary_drift = QLabel("primary std graph")
        graph_secondary_standard = QLabel("Secondary std graph")

        layout.addWidget(graph_primary_drift)
        layout.addWidget(graph_secondary_standard)

        return layout
