import time

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, QRadioButton
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from src.utils import gui_utils
from src.view.ratio_box_widget import RatioBoxWidget


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method.ratios[0]
        self.drift_coefficient = self.data_processing_dialog.model.drift_coefficient
        self.drift_intercept = self.data_processing_dialog.model.drift_y_intercept

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)
        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_widget_contents)

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

        graph_widget = self._create_graph_widget(self.ratio)

        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)
        self.ratio_radiobox_widget.set_ratio(self.ratio)

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(graph_widget)

        return layout

    def _create_graph_widget(self, ratio):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.primary_drift_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.secondary_check_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self._create_primary_drift_graph(self.primary_sample, self.primary_drift_axis, ratio)
        self._create_secondary_check_graph(self.secondary_sample, self.secondary_check_axis, ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

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

    def update_widget_contents(self):
        self.update_graphs(self.ratio)

    ################
    ### Plotting ###
    ################

    def _create_primary_drift_graph(self, sample, axis, ratio):
        axis.clear()
        axis.set_title("Primary ref. material: " + sample.name + "\nraw delta", loc="left")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        xs = []
        ys = []
        yerrors = []
        xs_removed = []
        ys_removed = []
        yerrors_removed = []

        for spot in sample.spots:
            if spot.not_corrected_deltas[ratio.delta_name][0]:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.not_corrected_deltas[ratio.delta_name][0])
                    yerrors.append(spot.not_corrected_deltas[ratio.delta_name][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.not_corrected_deltas[ratio.delta_name][0])
                    yerrors_removed.append(spot.not_corrected_deltas[ratio.delta_name][1])

                axis.set_ylabel(ratio.delta_name)
            else:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                axis.set_ylabel(ratio.name)

        y_mean = np.mean(ys)
        y_stdev = np.std(ys)
        label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")
        axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour, label=label)
        axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o", markeredgecolor=sample.colour,
                      markerfacecolor="none")

        drift_coefficient = self.drift_coefficient[ratio]
        drift_intercept = self.drift_intercept[ratio]
        if drift_coefficient:
            y_line = [(drift_intercept + (drift_coefficient * time.mktime(x.timetuple()))) for x in xs]
            y_line_label = "y = " + "{:.3e}".format(drift_coefficient) + "x + " + format(drift_intercept, ".1f")

            axis.plot(xs, y_line, marker="", label=y_line_label)

        axis.set_xlabel("Time")
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()
        axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))

    def _create_secondary_check_graph(self, sample, axis, ratio):
        axis.clear()
        axis.set_title("Secondary ref. material: " + sample.name + "\n drift corrected delta", loc="left")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        xs = []
        ys = []
        yerrors = []

        xs_removed = []
        ys_removed = []
        yerrors_removed = []

        for spot in sample.spots:
            if spot.drift_corrected_deltas[ratio.delta_name][0]:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.drift_corrected_deltas[ratio.delta_name][0])
                    yerrors.append(spot.drift_corrected_deltas[ratio.delta_name][1])
                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.drift_corrected_deltas[ratio.delta_name][0])
                    yerrors_removed.append(spot.drift_corrected_deltas[ratio.delta_name][1])

                axis.set_ylabel(ratio.delta_name)
            else:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors.append(spot.mean_two_st_error_isotope_ratios[ratio][1])
                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                axis.set_ylabel(ratio.name)
        y_mean = np.mean(ys)
        y_stdev = np.std(ys)
        label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")

        axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour, label=label)
        axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o", markeredgecolor=sample.colour,
                      markerfacecolor="none")
        axis.set_xlabel("Time")
        axis.set_ylabel(ratio.delta_name)
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()
        axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))
