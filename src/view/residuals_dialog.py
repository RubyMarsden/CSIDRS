import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QFrame
from matplotlib import pyplot as plt

from utils import gui_utils
from view.ratio_box_widget import RatioBoxWidget


class ResidualsDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Residuals and correlation coefficient summary")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog

        self.ratio = data_processing_dialog.get_current_ratio()
        # Create the ratio selection button here - because the button must exist before ratio can change.
        self.ratio_selection_widget = self._create_ratio_selection_widget()

        self.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.ratio_selection_widget)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self._create_graph_widget(), 8)
        lower_layout.addWidget(self._create_regression_results_summary_widget(), 2)

        self._create_residuals_graph()

        layout.addLayout(lower_layout)
        self.setLayout(layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios)
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=False)

        return self.ratio_radiobox_widget

    def _create_graph_widget(self):
        self.fig = plt.figure()

        self.residuals_axis = self.fig.add_subplot()

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

    def _create_regression_results_summary_widget(self):
        regression_results_widget = QWidget()
        layout = QVBoxLayout()
        residual_explanation_text = QLabel("The residual graph shows the true value - expected value from the model. "
                                           "If there is a noticeable trend in the residual graph then it suggests "
                                           "that there is an additional aspect to the modelling that could have been "
                                           "missed.")
        font_family = residual_explanation_text.font().family()
        font = QFont(font_family, 8)

        residual_explanation_text.setWordWrap(True)
        residual_explanation_text.setFont(font)

        layout.addWidget(residual_explanation_text)

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        h_line.setLineWidth(1)

        layout.addWidget(h_line)

        regression_results_widget.setLayout(layout)

        return regression_results_widget

    ################
    ### Plotting ###
    ################

    def _create_residuals_graph(self):
        self.residuals_axis.clear()
        self.residuals_axis.set_title("Residuals", loc="left")
        self.residuals_axis.spines['top'].set_visible(False)
        self.residuals_axis.spines['right'].set_visible(False)
        drift_coef = self.data_processing_dialog.model.calculation_results.all_ratio_results[self.ratio].drift_coefficient
        y_intercept = self.data_processing_dialog.model.calculation_results.all_ratio_results[self.ratio].drift_y_intercept
        times_from_model = np.array(self.data_processing_dialog.model.calculation_results.all_ratio_results[self.ratio].get_primary_rm_times())
        times = times_from_model.reshape(1, len(times_from_model))
        drift_coef = drift_coef.reshape(len(drift_coef), 1)
        array_for_y_intercept = np.full(shape=(1, len(times)), fill_value=1)

        y_int = y_intercept.reshape(len(y_intercept), 1) * array_for_y_intercept

        predicted_values = (drift_coef * times) + y_int
        predicted_values = np.transpose(predicted_values)

        true_values = self.data_processing_dialog.model.calculation_results.all_ratio_results[self.ratio].get_primary_rm_data_for_drift_corr()
        residuals = true_values - predicted_values

        number_data_points = len(residuals[0])

        predicted_means = list(np.mean(predicted_values, axis=1))

        residuals_means = list(np.mean(residuals, axis=1))

        histogram_range = np.vstack((np.min(residuals, axis=1), np.max(residuals, axis=1)))
        histogram_range = np.transpose(histogram_range)
        histogram_data = [np.histogram(residuals[i], 'fd')[0] for i in range(residuals.shape[0])]

        maximum_binned_data = max([max(binned_data) for binned_data in histogram_data])

        sensible_factor = min(np.diff(predicted_means)) / maximum_binned_data

        for predicted_mean, binned_data, h_range in zip(predicted_means, histogram_data, histogram_range):
            binned_data = binned_data * sensible_factor
            lefts = predicted_mean - 0.5 * binned_data
            number_of_bin_edges = len(binned_data) + 1
            bin_edges = np.linspace(h_range[0], h_range[1], number_of_bin_edges)
            heights = np.diff(bin_edges)
            centres = bin_edges[:-1] + heights / 2

            self.residuals_axis.barh(centres, binned_data, height=heights, left=lefts, alpha=0.5)

        self.residuals_axis.scatter(predicted_means, residuals_means)

        self.residuals_axis.set_xlabel("Fitted values")
        self.residuals_axis.set_ylabel("Residuals")

        self.fig.tight_layout()

    ###############
    ### Actions ###
    ###############

    def on_ratio_changed(self, ratio):
        self.ratio = ratio
        self._create_residuals_graph()
        self.canvas.draw()

