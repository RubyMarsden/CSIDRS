import time

import matplotlib.dates as mdates
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QRadioButton, QPushButton
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

from model.drift_correction_type import DriftCorrectionType
from utils import gui_utils
from view.further_MLR_dialog import FurtherMultipleLinearRegressionDialog
from view.ratio_box_widget import RatioBoxWidget
from view.residuals_dialog import ResidualsDialog


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.rhs_layout = None
        self.linear_regression_text_widget = None
        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method.ratios[0]

        # Create the ratio selection button here - because the button must exist before ratio can change.
        self._create_ratio_selection_widget()

        self.drift_coefficient = self.data_processing_dialog.model.drift_coefficient_by_ratio
        self.drift_intercept = self.data_processing_dialog.model.drift_y_intercept_by_ratio

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)
        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_widget_contents)
        self.data_processing_dialog.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_changed)
        self.layout = QHBoxLayout()

        for sample in self.data_processing_dialog.samples:
            if sample.is_primary_reference_material:
                self.primary_sample = sample
            elif sample.is_secondary_reference_material:
                self.secondary_sample = sample
            elif self.data_processing_dialog.model.secondary_reference_material == "No secondary reference material":
                self.secondary_sample = None

        self.graph_widget = self._create_graph_widget(self.ratio)

        self.linear_regression_text_widget = self._create_linear_text_widget(self.ratio)

        self.no_drift_radio_button = QRadioButton("Drift correction off")
        self.no_drift_radio_button.toggled.connect(self.drift_type_changed)
        self.drift_radio_button = QRadioButton("Linear drift correction on")
        self.drift_radio_button.toggled.connect(self.drift_type_changed)

        self.rhs_layout = self._create_rhs_layout()
        self.lhs_layout = self._create_lhs_layout()
        self.no_drift_radio_button.setChecked(True)

        self.layout.addLayout(self.lhs_layout, 4)
        self.layout.addLayout(self.rhs_layout, 6)

        self.setLayout(self.layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=False)

        return self.ratio_radiobox_widget

    def _create_rhs_layout(self):
        rhs_layout = QHBoxLayout()
        rhs_layout.addWidget(self.graph_widget)

        return rhs_layout

    def _create_lhs_layout(self):
        lhs_layout = QVBoxLayout()
        lhs_layout.addWidget(self.ratio_radiobox_widget)
        lhs_layout.addWidget(self.linear_regression_text_widget)
        lhs_layout.addWidget(self.drift_radio_button)

        lhs_layout.addWidget(self.no_drift_radio_button)

        more_information_button_layout = self._create_more_information_buttons_layout()
        lhs_layout.addLayout(more_information_button_layout)
        more_information_button_layout.setAlignment(Qt.AlignLeft)

        return lhs_layout

    def _create_linear_text_widget(self, ratio):
        widget = QWidget()
        linear_r_squared = self.data_processing_dialog.model.statsmodel_result_by_ratio[ratio].rsquared
        linear_adj_r_squared = self.data_processing_dialog.model.statsmodel_result_by_ratio[ratio].rsquared_adj
        linear_gradient = self.data_processing_dialog.model.drift_coefficient_by_ratio[ratio]
        linear_gradient_st_error = self.data_processing_dialog.model.statsmodel_result_by_ratio[ratio].bse[1]

        info_layout = QVBoxLayout()

        explanation_text = QLabel(
            "The information below is a summary of the statistics provided from the statsmodels python package "
            "ordinary least squares regression module. Further information about these statistics can be found by "
            "selecting the 'Residuals and statsmodels statistics summary' button. Any guidelines below on "
            "interpreting these statistics come from Frost (2019)")
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
        self.r_squared_text = QLabel("R<sup>2</sup>: " + format(linear_r_squared, ".3f"))
        self.r_squared_text.setWordWrap(True)
        self.r_squared_text.setFont(font)
        adj_r_squared_explanation_text = QLabel(
            "Adjusted R<sup>2</sup> takes into account the number of terms in the model - adding more terms to "
            "multiple linear regression analysis always increases the R<sup>2</sup> value.")
        adj_r_squared_explanation_text.setWordWrap(True)
        adj_r_squared_explanation_text.setFont(font)
        self.adj_r_squared_text = QLabel("Adjusted R<sup>2</sup>: " + format(linear_adj_r_squared, ".3f"))
        self.adj_r_squared_text.setWordWrap(True)
        self.adj_r_squared_text.setFont(font)
        self.linear_gradient_value_text = QLabel(
            "Gradient of calculated linear drift: " + "{:.3e}".format(linear_gradient))
        self.linear_gradient_value_text.setWordWrap(True)
        self.linear_gradient_value_text.setFont(font)
        linear_gradient_st_error_explanation_text = QLabel("Explain the st error here")
        linear_gradient_st_error_explanation_text.setWordWrap(True)
        linear_gradient_st_error_explanation_text.setFont(font)
        self.linear_gradient_standard_error_text = QLabel(
            "Standard error on the gradient: " + "{:.3e}".format(linear_gradient_st_error))
        self.linear_gradient_standard_error_text.setWordWrap(True)
        self.linear_gradient_standard_error_text.setFont(font)

        info_layout.addWidget(explanation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(citation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.r_squared_text, alignment=Qt.AlignTop)
        info_layout.addWidget(adj_r_squared_explanation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.adj_r_squared_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.linear_gradient_value_text, alignment=Qt.AlignTop)
        info_layout.addWidget(linear_gradient_st_error_explanation_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.linear_gradient_standard_error_text, alignment=Qt.AlignTop)

        widget.setLayout(info_layout)
        return widget

    def _create_more_information_buttons_layout(self):
        layout = QHBoxLayout()
        residuals_button = QPushButton("Residual graph")
        residuals_button.clicked.connect(self.on_residual_button_pushed)

        operators_button = QPushButton("Developers - MLR")
        operators_button.clicked.connect(self.on_operators_button_pushed)

        layout.addWidget(residuals_button, alignment=Qt.AlignLeft)
        layout.addWidget(operators_button, alignment=Qt.AlignLeft)
        return layout

    def _create_graph_widget(self, ratio):
        self.fig = plt.figure()

        self.grid_spec = GridSpec(3, 1)
        self.primary_drift_axis = self.fig.add_subplot(self.grid_spec[0])
        self.primary_drift_corrected_axis = self.fig.add_subplot(self.grid_spec[1])
        self.secondary_check_axis = self.fig.add_subplot(self.grid_spec[2])

        self._create_primary_drift_graph(self.primary_sample, ratio)
        self._create_primary_drift_corrected_graph(self.primary_sample, ratio)
        self._create_secondary_check_graph(self.secondary_sample, ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

    ###############
    ### Actions ###
    ###############

    def on_sample_tree_item_changed(self, current_item, previous_tree_item):
        self.highlight_selected_ratio_data_point(current_item, previous_tree_item)

    def update_graphs(self, ratio):
        self.primary_drift_axis.clear()
        self.primary_drift_corrected_axis.clear()
        self.secondary_check_axis.clear()

        self._create_primary_drift_graph(self.primary_sample, ratio)
        self._create_primary_drift_corrected_graph(self.primary_sample, ratio)
        self._create_secondary_check_graph(self.secondary_sample, ratio)

        self.canvas.draw()

    def change_ratio(self, ratio):
        self.ratio = ratio
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=True)

        self.update_widget_contents()
        if self.data_processing_dialog.model.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN:
            self.drift_radio_button.setChecked(True)
            self.no_drift_radio_button.setChecked(False)
        else:
            self.drift_radio_button.setChecked(False)
            self.no_drift_radio_button.setChecked(True)

    def update_widget_contents(self):
        linear_r_squared = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].rsquared
        linear_adj_r_squared = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].rsquared_adj
        linear_gradient = self.data_processing_dialog.model.drift_coefficient_by_ratio[self.ratio]
        linear_gradient_st_error = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].bse[1]

        self.r_squared_text.setText("R<sup>2</sup>: " + format(linear_r_squared, ".3f"))
        self.adj_r_squared_text.setText("Adjusted R<sup>2</sup>: " + format(linear_adj_r_squared, ".3f"))
        self.linear_gradient_value_text.setText(
            "Gradient of calculated linear drift: " + "{:.3e}".format(linear_gradient))
        self.linear_gradient_standard_error_text.setText(
            "Standard error on the gradient: " + "{:.3e}".format(linear_gradient_st_error))

        self.update_graphs(self.ratio)

    def on_residual_button_pushed(self):
        dialog = ResidualsDialog(self.data_processing_dialog, self.ratio)
        result = dialog.exec()

    def on_operators_button_pushed(self):
        dialog = FurtherMultipleLinearRegressionDialog(self.data_processing_dialog)
        result = dialog.exec()

    def drift_type_changed(self):
        if self.drift_radio_button.isChecked():
            drift_correction_type = DriftCorrectionType.LIN
        else:
            drift_correction_type = DriftCorrectionType.NONE

        self.data_processing_dialog.model.signals.driftCorrectionChanged.emit(self.ratio, drift_correction_type)

    def highlight_selected_ratio_data_point(self, current_item, previous_tree_item):
        if current_item is None or current_item.is_sample:
            self.primary_drift_axis.clear()
            self.update_graphs(self.ratio)
        else:
            current_spot = current_item.spot
            if previous_tree_item is None or previous_tree_item.is_sample:
                self.primary_drift_axis.clear()
                self.update_graphs(self.ratio)
                previous_spot = None
            else:
                previous_spot = previous_tree_item.spot
            primary_xs = []
            primary_ys = []
            for spot in self.primary_sample.spots:
                primary_ys.append(spot.not_corrected_deltas[self.ratio][0])
                primary_xs.append(spot)

            if self.secondary_sample:
                secondary_xs = []
                secondary_ys = []
                for spot in self.secondary_sample.spots:
                    if self.ratio.has_delta:
                        secondary_ys.append(spot.not_corrected_deltas[self.ratio][0])
                    else:
                        secondary_ys.append(spot.mean_two_st_error_isotope_ratios[self.ratio][0])
                    secondary_xs.append(spot)

                for secondary_x, secondary_y in zip(secondary_xs, secondary_ys):
                    if secondary_x == current_spot:
                        if current_spot.is_flagged:
                            self.secondary_check_axis.errorbar(secondary_x.datetime, secondary_y, ls="", marker="o",
                                                               markerfacecolor=None, markeredgecolor="yellow")
                        else:
                            self.secondary_check_axis.errorbar(secondary_x.datetime, secondary_y, ls="", marker="o",
                                                               color="yellow")

                    if secondary_x == previous_spot:
                        if current_spot.is_flagged:
                            self.secondary_check_axis.errorbar(secondary_x.datetime, secondary_y, ls="", marker="o",
                                                               markerfacecolor=None,
                                                               markeredgecolor=self.secondary_sample.colour)
                        else:
                            self.secondary_check_axis.errorbar(secondary_x.datetime, secondary_y, ls="", marker="o",
                                                               color=self.secondary_sample.colour)

            for primary_x, primary_y in zip(primary_xs, primary_ys):
                if primary_x == current_spot:
                    self.primary_drift_axis.errorbar(primary_x.datetime, primary_y, ls="", marker="o", color="yellow")

                if primary_x == previous_spot:
                    self.primary_drift_axis.errorbar(primary_x.datetime, primary_y, ls="", marker="o",
                                                     color=self.primary_sample.colour)

        self.canvas.draw()

    ################
    ### Plotting ###
    ################

    def _create_primary_drift_graph(self, sample, ratio):
        self.primary_drift_axis.clear()
        self.primary_drift_axis.set_title("Primary ref. material: " + sample.name + "\nraw delta", loc="left")
        self.primary_drift_axis.spines['top'].set_visible(False)
        self.primary_drift_axis.spines['right'].set_visible(False)

        xs = []
        ys = []
        yerrors = []
        xs_removed = []
        ys_removed = []
        yerrors_removed = []

        for spot in sample.spots:
            if ratio.has_delta:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.not_corrected_deltas[ratio][0])
                    yerrors.append(spot.not_corrected_deltas[ratio][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.not_corrected_deltas[ratio][0])
                    yerrors_removed.append(spot.not_corrected_deltas[ratio][1])

                self.primary_drift_axis.set_ylabel(ratio.delta_name())
            else:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    yerrors_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                self.primary_drift_axis.set_ylabel(ratio.name())

        y_mean = np.mean(ys)
        y_stdev = np.std(ys)
        label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")
        self.primary_drift_axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour, label=label)
        self.primary_drift_axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                                         markeredgecolor=sample.colour,
                                         markerfacecolor="none")

        drift_coefficient = self.drift_coefficient[ratio]
        drift_intercept = self.drift_intercept[ratio]
        if drift_coefficient:
            y_line = [(drift_intercept + (drift_coefficient * time.mktime(x.timetuple()))) for x in xs]
            y_line_label = "y = " + "{:.3e}".format(drift_coefficient) + "x + " + format(drift_intercept, ".1f")

            self.primary_drift_axis.plot(xs, y_line, marker="", label=y_line_label, color=sample.colour)

        self.primary_drift_axis.set_xlabel("Time")
        for x_tick_label in self.primary_drift_axis.get_xticklabels():
            x_tick_label.set_rotation(30)
            x_tick_label.set_horizontalalignment('right')

        self.primary_drift_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        self.fig.tight_layout()
        self.primary_drift_axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))

    def _create_primary_drift_corrected_graph(self, sample, ratio):
        self.primary_drift_corrected_axis.clear()
        self.primary_drift_corrected_axis.set_title("Primary ref. material: " + sample.name + "\ndrift corrected delta",
                                                    loc="left")
        self.primary_drift_corrected_axis.spines['top'].set_visible(False)
        self.primary_drift_corrected_axis.spines['right'].set_visible(False)

        xs = []
        ys = []
        yerrors = []
        xs_removed = []
        ys_removed = []
        yerrors_removed = []

        for spot in sample.spots:
            if ratio.has_delta:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.drift_corrected_deltas[ratio][0])
                    yerrors.append(spot.drift_corrected_deltas[ratio][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.drift_corrected_deltas[ratio][0])
                    yerrors_removed.append(spot.drift_corrected_deltas[ratio][1])

                self.primary_drift_corrected_axis.set_ylabel(ratio.delta_name())
            else:
                if not spot.is_flagged:
                    xs.append(spot.datetime)
                    ys.append(spot.drift_corrected_ratio_values_by_ratio[ratio][0])
                    yerrors.append(spot.drift_corrected_ratio_values_by_ratio[ratio][1])

                else:
                    xs_removed.append(spot.datetime)
                    ys_removed.append(spot.drift_corrected_ratio_values_by_ratio[ratio][0])
                    yerrors_removed.append(spot.drift_corrected_ratio_values_by_ratio[ratio][1])

                self.primary_drift_corrected_axis.set_ylabel(ratio.name())
        self.primary_drift_corrected_axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour)
        self.primary_drift_corrected_axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                                                   markeredgecolor=sample.colour,
                                                   markerfacecolor="none")

        self.primary_drift_corrected_axis.set_xlabel("Time")
        for x_tick_label in self.primary_drift_corrected_axis.get_xticklabels():
            x_tick_label.set_rotation(30)
            x_tick_label.set_horizontalalignment('right')

        self.primary_drift_corrected_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        self.fig.tight_layout()

    def _create_secondary_check_graph(self, sample, ratio):
        self.secondary_check_axis.clear()
        if not sample:
            self.secondary_check_axis.annotate("No secondary reference material", (0.28, 0.5))
            self.secondary_check_axis.set_xlim(0, 1)
            self.secondary_check_axis.set_ylim(0, 1)
        else:
            self.secondary_check_axis.set_title("Secondary ref. material: " + sample.name + "\n drift corrected delta",
                                                loc="left")
            self.secondary_check_axis.spines['top'].set_visible(False)
            self.secondary_check_axis.spines['right'].set_visible(False)

            xs = []
            ys = []
            yerrors = []

            xs_removed = []
            ys_removed = []
            yerrors_removed = []

            for spot in sample.spots:
                if ratio in spot.drift_corrected_deltas:
                    if not spot.is_flagged:
                        xs.append(spot.datetime)
                        ys.append(spot.drift_corrected_deltas[ratio][0])
                        yerrors.append(spot.drift_corrected_deltas[ratio][1])
                    else:
                        xs_removed.append(spot.datetime)
                        ys_removed.append(spot.drift_corrected_deltas[ratio][0])
                        yerrors_removed.append(spot.drift_corrected_deltas[ratio][1])

                    self.secondary_check_axis.set_ylabel(ratio.delta_name())
                else:
                    if not spot.is_flagged:
                        xs.append(spot.datetime)
                        ys.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                        yerrors.append(spot.mean_two_st_error_isotope_ratios[ratio][1])
                    else:
                        xs_removed.append(spot.datetime)
                        ys_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                        yerrors_removed.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                    self.secondary_check_axis.set_ylabel(ratio.name())
            y_mean = np.mean(ys)
            y_stdev = np.std(ys)
            label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")

            self.secondary_check_axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour,
                                               label=label)
            self.secondary_check_axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                                               markeredgecolor=sample.colour,
                                               markerfacecolor="none")
            self.secondary_check_axis.set_xlabel("Time")
            self.secondary_check_axis.set_ylabel(ratio.delta_name())

            for x_tick_label in self.secondary_check_axis.get_xticklabels():
                x_tick_label.set_rotation(30)
                x_tick_label.set_horizontalalignment('right')

            self.secondary_check_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        if self.secondary_sample:
            self.secondary_check_axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))
        self.fig.tight_layout()
