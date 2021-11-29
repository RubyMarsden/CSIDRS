from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, QTreeWidgetItemIterator, \
    QRadioButton
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from src.utils import gui_utils
from src.view.ratio_box_widget import RatioBoxWidget


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method_dictionary["ratios"][0]

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)

        layout = QHBoxLayout()

        for sample in self.data_processing_dialog.samples:
            if sample.is_primary_reference_material:
                self.primary_sample = sample
            elif sample.is_secondary_reference_material:
                self.secondary_sample = sample

        lhs_layout = self._create_lhs_layout()
        rhs_layout = self._create_rhs_layout()

        layout.addLayout(lhs_layout)
        layout.addLayout(rhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        reference_material_table = QTableWidget()
        layout.addWidget(reference_material_table)
        drift_explanation_text = QLabel("This explains why the drift is on or off and what it is etc")
        drift_explanation_text.setWordWrap(True)
        no_drift_radio_button = QRadioButton("Drift correction off")
        drift_radio_button = QRadioButton("Linear drift correction on")
        layout.addWidget(drift_explanation_text)
        layout.addWidget(no_drift_radio_button)
        layout.addWidget(drift_radio_button)

        return layout

    def _create_rhs_layout(self):
        layout = QVBoxLayout()

        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method_dictionary["ratios"],
                                                    self.data_processing_dialog.model.signals)

        graph_widget = self._create_graph_widget(self.ratio)

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(graph_widget)

        return layout

    def _create_graph_widget(self, ratio):
        graph = QWidget()
        layout = QVBoxLayout()

        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.primary_drift_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.secondary_check_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self._create_primary_drift_graph(self.primary_sample, self.primary_drift_axis, ratio)
        self._create_secondary_check_graph(self.secondary_sample, self.secondary_check_axis, ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph
    ###############
    ### Actions ###
    ###############

    def update_graphs(self, ratio):
        self.primary_drift_axis.clear()
        self.secondary_check_axis.clear()

        self._create_primary_drift_graph(self.primary_sample, self.primary_drift_axis, ratio)
        self._create_secondary_check_graph(self.secondary_sample, self.secondary_check_axis, ratio)

        self.canvas.draw()

    def change_ratio(self, ratio):
        self.ratio = ratio
        self.update_graphs(ratio)


    ################
    ### Plotting ###
    ################


    def _create_primary_drift_graph(self, sample, axis, ratio):
        axis.clear()
        axis.set_title("Primary reference material raw data for drift correction")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        xs = [spot.datetime for spot in sample.spots]
        ys = [spot.not_corrected_deltas[ratio.delta_name][0] for spot in sample.spots]
        yerrors = [spot.not_corrected_deltas[ratio.delta_name][1] for spot in sample.spots]

        axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("Time")
        axis.set_ylabel(ratio.delta_name)
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()

    def _create_secondary_check_graph(self, sample, axis, ratio):

        axis.clear()
        axis.set_title("Secondary reference material with drift correction")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        xs = [spot.datetime for spot in sample.spots]
        ys = [spot.drift_corrected_deltas[ratio.delta_name][0] for spot in sample.spots]
        yerrors = [spot.drift_corrected_deltas[ratio.delta_name][1] for spot in sample.spots]

        axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("Time")
        axis.set_ylabel(ratio.delta_name)
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()
