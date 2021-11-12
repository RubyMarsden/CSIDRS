from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, QTreeWidgetItemIterator
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

from src.utils import gui_utils


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        layout = QHBoxLayout()

        self.primary_sample = [
            sample for sample in data_processing_dialog.samples if sample.is_primary_reference_material
        ]
        self.secondary_sample = [
            sample for sample in data_processing_dialog.samples if sample.is_secondary_reference_material
        ]

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

        graph_widget = self._create_graph_widget()

        layout.addWidget(graph_primary_drift)
        layout.addWidget(graph_secondary_standard)
        layout.addWidget(graph_widget)

        return layout

    def _create_graph_widget(self):
        graph = QWidget()
        layout = QVBoxLayout()

        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        # self.spot_invisible_grid_spec = GridSpec(1, 1)
        self.primary_drift_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.secondary_check_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self._create_primary_drift_graph(self.primary_sample, self.primary_drift_axis, "18O/16O")
        # self.create_secondary_reference_material_check_graph(self.secondary_sample, self.secondary_check_axis)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph

    def _create_primary_drift_graph(self, sample, axis, ratio_name):
        axis.clear()
        xs = []
        ys = []
        yerrors = []
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for spot in sample[0].spots:
            ys.append(spot.mean_st_error_isotope_ratios[ratio_name][0])
            yerrors.append(spot.mean_st_error_isotope_ratios[ratio_name][1])
            xs.append(spot.datetime)

        axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o")
        axis.set_xlabel("Time")
        axis.set_ylabel(ratio_name)
        plt.tight_layout()

