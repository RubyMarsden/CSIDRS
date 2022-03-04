import time

import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTableWidget, QRadioButton, QPushButton
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from src.utils import gui_utils
from src.view.ratio_box_widget import RatioBoxWidget


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.linear_regression_widget = None
        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method.ratios[0]

        # Create the ratio selection button here - because the button must exist before ratio can change.
        self.ratio_selection_widget = self._create_ratio_selection_widget()

        self.drift_coefficient = self.data_processing_dialog.model.drift_coefficient
        self.drift_intercept = self.data_processing_dialog.model.drift_y_intercept

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)
        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_widget_contents)

        self.layout = QVBoxLayout()

        for sample in self.data_processing_dialog.samples:
            if sample.is_primary_reference_material:
                self.primary_sample = sample
            elif sample.is_secondary_reference_material:
                self.secondary_sample = sample
            elif self.data_processing_dialog.model.secondary_reference_material == "No secondary reference material":
                self.secondary_sample = None

        ratio_selection_widget = self._create_linear_regression_widget()
        linear_regression_widget = self.linear_regression_widget
        more_information_button_layout = self._create_more_information_button_layout()

        self.layout.addWidget(ratio_selection_widget)
        self.layout.addWidget(linear_regression_widget)
        self.layout.addLayout(more_information_button_layout)

        self.setLayout(self.layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)
        self.ratio_radiobox_widget.set_ratio(self.ratio)

        return self.ratio_radiobox_widget

    def _create_linear_regression_widget(self):
        self.linear_regression_widget = QWidget()

        layout = QHBoxLayout()

        graph_widget = self._create_graph_widget(self.ratio)

        linear_r_squared = self.data_processing_dialog.model.linear_rsquared
        linear_adj_r_squared = self.data_processing_dialog.model.linear_rsquared_adj

        info_layout = QVBoxLayout()

        explanation_text = QLabel(
            "The information below is a summary of the statistics provided from the statsmodel python package "
            "ordinary least squares regression module. If the user suspects that the linear drift correction is not "
            "appropriate for their data then further information about these statistics can be found by selecting the "
            "'More information' button and asking the CAMECA 1280 operator. Any guidelines below on interpreting "
            "these statistics come from Frost (2019)")
        font_family = explanation_text.font().family()
        font = QFont(font_family, 9)
        explanation_text.setWordWrap(True)
        explanation_text.setFont(font)
        citation_text = QLabel(
            "Frost, J., 2019. Regression analysis: An intuitive guide for using and interpreting linear "
            "models. Statisics By Jim Publishing.")
        font_italic = QFont(font_family, 8)
        font_italic.setItalic(True)
        citation_text.setWordWrap(True)
        citation_text.setFont(font_italic)
        r_squared_text = QLabel("R<sup>2</sup>: " + format(linear_r_squared, ".3f"))
        r_squared_text.setWordWrap(True)
        adj_r_squared_explanation_text = QLabel(
            "Adjusted R<sup>2</sup> takes into account the number of terms in the model - adding more terms to multiple linear regression analysis always increases the R<sup>2</sup> value.")
        adj_r_squared_explanation_text.setWordWrap(True)
        adj_r_squared_explanation_text.setFont(font)
        adj_r_squared_text = QLabel("Adjusted R<sup>2</sup>: " + format(linear_adj_r_squared, ".3f"))
        adj_r_squared_text.setWordWrap(True)
        self.no_drift_radio_button = QRadioButton("Drift correction off")
        self.drift_radio_button = QRadioButton("Linear drift correction on")

        info_layout.addWidget(explanation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(citation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(r_squared_text, alignment=Qt.AlignTop)
        info_layout.addWidget(adj_r_squared_explanation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(adj_r_squared_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.no_drift_radio_button)
        info_layout.addWidget(self.drift_radio_button)

        layout.addLayout(info_layout, 3.5)
        layout.addWidget(graph_widget, 6.5)

        self.linear_regression_widget.setLayout(layout)

    def _create_more_information_button_layout(self):
        layout = QHBoxLayout()
        button = QPushButton("More information")

        layout.addWidget(button, alignment=Qt.AlignLeft)
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
        self.linear_regression_widget.removeWidget()
        self._create_linear_regression_widget()

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
        if not sample:
            axis.annotate("No secondary reference material", (0.28, 0.5))
            axis.set_xlim(0, 1)
            axis.set_ylim(0, 1)
        else:
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
            axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                          markeredgecolor=sample.colour,
                          markerfacecolor="none")
            axis.set_xlabel("Time")
            axis.set_ylabel(ratio.delta_name)
            plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

            axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

            plt.tight_layout()
            axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))
