import time

import matplotlib.dates as mdates
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QRadioButton, QPushButton, QTabWidget
from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec

from controllers.signals import signals
from model.drift_correction_type import DriftCorrectionType
from utils import gui_utils
from view.further_MLR_dialog import FurtherMultipleLinearRegressionDialog
from view.residuals_dialog import ResidualsDialog


class DriftCorrectionWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.rhs_layout = None
        self.linear_regression_text_widget = None
        self.data_processing_dialog = data_processing_dialog
        self.model = data_processing_dialog.model

        self.data_processing_dialog.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)
        signals.dataRecalculated.connect(self.on_data_recalculated)
        self.data_processing_dialog.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_changed)
        self.layout = QHBoxLayout()

        self.primary_sample = self.data_processing_dialog.model.primary_reference_material
        self.secondary_sample = self.data_processing_dialog.model.secondary_reference_material

        self.graph_tab_widget = self._create_graph_tab_widget()

        self.linear_regression_text_widget = self._create_linear_text_widget()

        self.no_drift_radio_button = QRadioButton("Drift correction off")
        self.no_drift_radio_button.setChecked(True)
        self.no_drift_radio_button.toggled.connect(self.drift_type_changed)
        self.drift_radio_button = QRadioButton("Linear drift\ncorrection on")
        self.drift_radio_button.toggled.connect(self.drift_type_changed)

        self.rhs_layout = self._create_rhs_layout()
        self.lhs_layout = self._create_lhs_layout()

        self.layout.addLayout(self.lhs_layout, 3)
        self.layout.addLayout(self.rhs_layout, 6)

        self.setLayout(self.layout)

    def _create_rhs_layout(self):
        rhs_layout = QHBoxLayout()
        rhs_layout.addWidget(self.graph_tab_widget)

        return rhs_layout

    def _create_lhs_layout(self):
        lhs_layout = QVBoxLayout()
        lhs_layout.addWidget(self.linear_regression_text_widget)
        lhs_layout.addWidget(self.drift_radio_button)

        lhs_layout.addWidget(self.no_drift_radio_button)

        more_information_button_layout = self._create_more_information_buttons_layout()
        lhs_layout.addLayout(more_information_button_layout)
        more_information_button_layout.setAlignment(Qt.AlignLeft)

        return lhs_layout

    def _create_linear_text_widget(self):
        widget = QWidget()

        info_layout = QVBoxLayout()
        section_title = QLabel("Statistics\n summary")
        font_family = section_title.font().family()
        font = QFont(font_family, 11)
        font_bold = QFont(font_family, 11)
        font_bold.setBold(True)
        section_title.setWordWrap(True)
        section_title.setFont(font_bold)

        self.r_squared_text = QLabel()
        self.r_squared_text.setWordWrap(True)
        self.r_squared_text.setFont(font)

        self.r_squared_uncertainty_range = QLabel()
        self.r_squared_uncertainty_range.setWordWrap(True)
        self.r_squared_uncertainty_range.setFont(font)

        self.linear_gradient_value_text = QLabel()
        self.linear_gradient_value_text.setWordWrap(True)
        self.linear_gradient_value_text.setFont(font)

        self.linear_gradient_uncertainty_text = QLabel()
        self.linear_gradient_uncertainty_text.setWordWrap(True)
        self.linear_gradient_uncertainty_text.setFont(font)

        info_layout.addWidget(section_title, alignment=Qt.AlignTop)
        info_layout.addWidget(self.r_squared_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.r_squared_uncertainty_range, alignment=Qt.AlignTop)
        info_layout.addWidget(self.linear_gradient_value_text, alignment=Qt.AlignTop)
        info_layout.addWidget(self.linear_gradient_uncertainty_text, alignment=Qt.AlignTop)

        widget.setLayout(info_layout)
        return widget

    def _create_more_information_buttons_layout(self):
        layout = QHBoxLayout()
        residuals_button = QPushButton("Residual graph")
        residuals_button.setToolTip("Further statistics provided by the statsmodels python package "
                                    "ordinary least squares regression module.")
        residuals_button.clicked.connect(self.on_residual_button_pushed)

        layout.addWidget(residuals_button, alignment=Qt.AlignLeft)

        return layout

    def _create_graph_tab_widget(self):
        primary_reference_material_graph_widget = self._create_primary_drift_graph_widget()
        secondary_reference_material_graph_widget = self._create_secondary_drift_graph_widget()

        graph_tab_widget = QTabWidget()
        graph_tab_widget.addTab(primary_reference_material_graph_widget, "Primary drift graph")
        graph_tab_widget.addTab(secondary_reference_material_graph_widget, "Secondary drift graph")

        return graph_tab_widget

    def _create_primary_drift_graph_widget(self):
        self.primary_drift_fig = plt.figure()

        self.primary_drift_axis = self.primary_drift_fig.add_subplot()
        graph_widget, self.primary_drift_canvas = gui_utils.create_figure_widget(self.primary_drift_fig, self)

        return graph_widget

    def _create_secondary_drift_graph_widget(self):
        self.secondary_check_fig = plt.figure()

        self.secondary_check_axis = self.secondary_check_fig.add_subplot()
        graph_widget, self.secondary_check_canvas = gui_utils.create_figure_widget(self.secondary_check_fig, self)

        return graph_widget

    ###############
    ### Actions ###
    ###############

    def on_sample_tree_item_changed(self, current_item, previous_tree_item):
        self.highlight_selected_ratio_data_point(current_item, previous_tree_item)

    def update_graphs(self, ratio):
        self.primary_drift_axis.clear()
        self.secondary_check_axis.clear()

        self._create_primary_drift_graph(self.primary_sample, ratio)
        self._create_secondary_check_graph(self.secondary_sample, ratio)

        self.primary_drift_canvas.draw()
        self.secondary_check_canvas.draw()

    def on_ratio_changed(self, ratio):
        self.update_stats_text(ratio)
        self.update_graphs(ratio)

        is_linear = self.model.drift_correction_type_by_ratio[ratio] == DriftCorrectionType.LIN
        self.drift_radio_button.setChecked(is_linear)
        self.no_drift_radio_button.setChecked(not is_linear)

    def on_data_recalculated(self):
        ratio = self.data_processing_dialog.get_current_ratio()
        self.update_stats_text(ratio)
        self.update_graphs(ratio)

    def update_stats_text(self, ratio):
        linear_r_squared_mc = \
        self.data_processing_dialog.model.calculation_results.all_ratio_results[ratio].linear_regression_result[0]
        linear_gradient_mc = self.data_processing_dialog.model.calculation_results.all_ratio_results[
            ratio].drift_coefficient

        linear_r_squared = np.mean(linear_r_squared_mc)
        linear_r_squared_median = np.median(linear_r_squared_mc)
        linear_r_squared_st_dev = np.std(linear_r_squared_mc)
        linear_gradient = np.mean(linear_gradient_mc)
        linear_gradient_st_dev = np.std(linear_gradient_mc)

        self.r_squared_text.setText("R<sup>2</sup>:\n" + format(linear_r_squared, ".3f"))
        self.r_squared_uncertainty_range.setText(
            "R<sup>2</sup> standard deviation:\n" + format(linear_r_squared_st_dev, ".3f"))
        self.linear_gradient_value_text.setText(
            "Gradient of calculated\nlinear drift:\n" + "{:.3e}".format(linear_gradient))
        self.linear_gradient_uncertainty_text.setText(
            "Gradient of calculated\nlinear drift standard deviation:\n" + "{:.3e}".format(linear_gradient_st_dev))

    def on_residual_button_pushed(self):
        dialog = ResidualsDialog(self.data_processing_dialog)
        result = dialog.exec()

    def drift_type_changed(self):
        if self.drift_radio_button.isChecked():
            drift_correction_type = DriftCorrectionType.LIN
        else:
            drift_correction_type = DriftCorrectionType.NONE

        current_ratio = self.data_processing_dialog.get_current_ratio()
        self.model.recalculate_data_with_drift_correction_changed(current_ratio, drift_correction_type)

    def highlight_selected_ratio_data_point(self, current_item, previous_tree_item):
        ratio = self.data_processing_dialog.get_current_ratio()
        t_zero = self.data_processing_dialog.model.calculation_results.get_t_zero()
        if current_item is None or current_item.is_sample:
            self.primary_drift_axis.clear()
            self.update_graphs(ratio)
        else:
            current_spot = current_item.spot
            if previous_tree_item is None or previous_tree_item.is_sample:
                self.primary_drift_axis.clear()
                self.update_graphs(ratio)
                previous_spot = None
            else:
                previous_spot = previous_tree_item.spot
            primary_spots = []
            primary_ys = []
            for spot in self.primary_sample.spots:
                if ratio.has_delta:
                    primary_ys.append(np.mean(spot.not_corrected_deltas[ratio]))
                else:
                    primary_ys.append(spot.mean_st_error_isotope_ratios[ratio][0])

                primary_spots.append(spot)

            if self.secondary_sample:
                secondary_spots = []
                secondary_ys = []
                for spot in self.secondary_sample.spots:
                    if ratio.has_delta:
                        secondary_ys.append(np.mean(spot.not_corrected_deltas[ratio]))
                    else:
                        secondary_ys.append(spot.mean_st_error_isotope_ratios[ratio][0])

                    secondary_spots.append(spot)

                for secondary_x, secondary_y in zip(secondary_spots, secondary_ys):
                    if secondary_x == current_spot:
                        x = secondary_x.datetime
                        if current_spot.is_flagged:
                            self.secondary_check_axis.errorbar(x, secondary_y, ls="", marker="o",
                                                               markerfacecolor=None, markeredgecolor="yellow")
                        else:
                            self.secondary_check_axis.errorbar(x, secondary_y, ls="", marker="o",
                                                               color="yellow")

                    if secondary_x == previous_spot:
                        x = secondary_x.datetime
                        if current_spot.is_flagged:
                            self.secondary_check_axis.errorbar(x, secondary_y, ls="", marker="o",
                                                               markerfacecolor=None,
                                                               markeredgecolor=self.secondary_sample.colour)
                        else:
                            self.secondary_check_axis.errorbar(x, secondary_y, ls="", marker="o",
                                                               color=self.secondary_sample.colour)

            for primary_x, primary_y in zip(primary_spots, primary_ys):
                x = time.mktime(primary_x.datetime.timetuple()) - t_zero
                if primary_x == current_spot:
                    self.primary_drift_axis.errorbar(x, primary_y, ls="", marker="o", color="yellow")

                if primary_x == previous_spot:
                    self.primary_drift_axis.errorbar(x, primary_y, ls="", marker="o",
                                                     color=self.primary_sample.colour)

        self.primary_drift_canvas.draw()
        self.secondary_check_canvas.draw()

    ################
    ### Plotting ###
    ################

    # def _create_primary_drift_graph(self, sample, ratio):

    def _create_primary_drift_graph(self, sample, ratio):
        self.primary_drift_axis.set_title("Primary ref. material: " + sample.name + "\nraw delta, 2sig uncertainty", loc="left")
        self.primary_drift_axis.spines['top'].set_visible(False)
        self.primary_drift_axis.spines['right'].set_visible(False)

        xs = []
        ys = []
        yerrors = []
        xs_removed = []
        ys_removed = []
        yerrors_removed = []

        t_zero = self.data_processing_dialog.model.calculation_results.get_t_zero()

        for spot in sample.spots:
            relative_time = time.mktime(spot.datetime.timetuple()) - t_zero
            if ratio.has_delta:
                if not spot.is_flagged:
                    xs.append(relative_time)
                    y = np.mean(spot.not_corrected_deltas[ratio])
                    dy = 2 * np.std(spot.not_corrected_deltas[ratio])
                    ys.append(y)
                    yerrors.append(dy)

                else:
                    xs_removed.append(relative_time)
                    y = np.mean(spot.not_corrected_deltas[ratio])
                    dy = 2 * np.std(spot.not_corrected_deltas[ratio])
                    ys_removed.append(y)
                    yerrors_removed.append(dy)

                axis_label = ratio.delta_name()

            else:
                if not spot.is_flagged:
                    xs.append(relative_time)
                    ys.append(spot.mean_st_error_isotope_ratios[ratio][0])
                    yerrors.append((2 * spot.mean_st_error_isotope_ratios[ratio][1]))

                else:
                    xs_removed.append(relative_time)
                    ys_removed.append(spot.mean_st_error_isotope_ratios[ratio][0])
                    yerrors_removed.append((2 * spot.mean_st_error_isotope_ratios[ratio][1]))

                axis_label = ratio.name()

        self.primary_drift_axis.set_ylabel(axis_label)

        y_mean = np.mean(ys)
        y_stdev = np.std(ys)
        label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")
        self.primary_drift_axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour, label=label)
        self.primary_drift_axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                                         markeredgecolor=sample.colour,
                                         markerfacecolor="none")

        drift_coefficient = np.mean(
            self.data_processing_dialog.model.calculation_results.all_ratio_results[ratio].drift_coefficient)
        drift_intercept = np.mean(
            self.data_processing_dialog.model.calculation_results.all_ratio_results[ratio].drift_y_intercept)
        if drift_coefficient:
            y_line = [(drift_intercept + (drift_coefficient * x)) for x in xs]

            self.primary_drift_axis.plot(xs, y_line, marker="", color=sample.colour)

        self.primary_drift_axis.set_xlabel("Time")
        for x_tick_label in self.primary_drift_axis.get_xticklabels():
            x_tick_label.set_rotation(10)
            x_tick_label.set_horizontalalignment('right')

        # self.primary_drift_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        self.primary_drift_fig.tight_layout()

        self.primary_drift_axis.legend(loc="upper left", bbox_to_anchor=(0.5, 1.0))

        if self.no_drift_radio_button.isChecked():
            return

        dc_xs = xs
        dc_ys = []
        dc_yerrors = []
        dc_xs_removed = xs_removed
        dc_ys_removed = []
        dc_yerrors_removed = []

        for spot in sample.spots:
            if not spot.is_flagged:
                y = np.mean(spot.drift_corrected_data[ratio])
                dy = 2 * np.std(spot.drift_corrected_data[ratio])
                dc_ys.append(y)
                dc_yerrors.append(dy)

            else:
                y = np.mean(spot.drift_corrected_data[ratio])
                dy = 2 * np.std(spot.drift_corrected_data[ratio])
                dc_ys_removed.append(y)
                dc_yerrors_removed.append(dy)

        dc_y_mean = np.mean(dc_ys)
        dc_y_stdev = np.std(dc_ys)
        dc_label = "Drift corrected data: \n Mean: " + format(dc_y_mean, ".3f") + ", St Dev: " + format(dc_y_stdev,
                                                                                                        ".3f")

        self.primary_drift_axis.errorbar(dc_xs, dc_ys, yerr=dc_yerrors, ls="", marker="s", color='r', label=dc_label)
        self.primary_drift_axis.errorbar(dc_xs_removed, dc_ys_removed, yerr=dc_yerrors_removed, ls="", marker="s",
                                         markeredgecolor='r',
                                         markerfacecolor="none"
                                         )

        self.primary_drift_axis.legend(loc="upper left", bbox_to_anchor=(0.5, 1.0))
        self.primary_drift_fig.tight_layout()

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
                if ratio.has_delta:
                    if not spot.is_flagged:
                        xs.append(spot.datetime)

                        y = np.mean(spot.drift_corrected_data[ratio])
                        dy = 2 * np.std(spot.drift_corrected_data[ratio])
                        ys.append(y)
                        yerrors.append(dy)
                    else:
                        xs_removed.append(spot.datetime)
                        y = np.mean(spot.drift_corrected_data[ratio])
                        dy = 2 * np.std(spot.drift_corrected_data[ratio])
                        ys_removed.append(y)
                        yerrors_removed.append(dy)
                else:
                    if not spot.is_flagged:
                        xs.append(spot.datetime)
                        ys.append(spot.mean_st_error_isotope_ratios[ratio][0])
                        yerrors.append((2 * spot.mean_st_error_isotope_ratios[ratio][1]))
                    else:
                        xs_removed.append(spot.datetime)
                        ys_removed.append(spot.mean_st_error_isotope_ratios[ratio][0])
                        yerrors_removed.append((2 * spot.mean_st_error_isotope_ratios[ratio][1]))

            y_mean = np.mean(ys)
            y_stdev = np.std(ys)
            label = "Mean: " + format(y_mean, ".3f") + ", St Dev: " + format(y_stdev, ".3f")

            self.secondary_check_axis.errorbar(xs, ys, yerr=yerrors, ls="", marker="o", color=sample.colour,
                                               label=label)
            self.secondary_check_axis.errorbar(xs_removed, ys_removed, yerr=yerrors_removed, ls="", marker="o",
                                               markeredgecolor=sample.colour,
                                               markerfacecolor="none")
            self.secondary_check_axis.set_xlabel("Time")
            y_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
            self.secondary_check_axis.set_ylabel(y_value_name)

            for x_tick_label in self.secondary_check_axis.get_xticklabels():
                x_tick_label.set_rotation(30)
                x_tick_label.set_horizontalalignment('right')

            self.secondary_check_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        if self.secondary_sample:
            self.secondary_check_axis.legend(loc="upper right", bbox_to_anchor=(1, 1.7))
        self.secondary_check_fig.tight_layout()
