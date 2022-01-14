from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QFrame
from matplotlib import pyplot as plt

from src.utils import gui_utils
from src.view.ratio_box_widget import RatioBoxWidget


class ResidualsDialog(QDialog):
    def __init__(self, data_processing_dialog, ratio):
        QDialog.__init__(self)
        self.setWindowTitle("Residuals and statsmodels statistics summary")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog

        self.ratio = ratio
        # Create the ratio selection button here - because the button must exist before ratio can change.
        self.ratio_selection_widget = self._create_ratio_selection_widget()

        layout = QVBoxLayout()
        layout.addWidget(self.ratio_selection_widget)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self._create_graph_widget(), 4)
        lower_layout.addWidget(self._create_regression_results_summary_widget(), 6)

        self._create_residuals_graph()

        layout.addLayout(lower_layout)
        self.setLayout(layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)
        self.ratio_radiobox_widget.set_ratio(self.ratio)

        return self.ratio_radiobox_widget

    def _create_graph_widget(self):
        self.fig = plt.figure()

        self.residuals_axis = plt.axes()

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

        summary_explanation_text = QLabel("The following parameters come from the python statsmodels package. They "
                                          "are listed here for completeness, however it is understood that users will "
                                          "not always be able to disregard linear drift if these parameters are not "
                                          "as expected as the model is simplified for usability.")
        summary_explanation_text.setWordWrap(True)
        summary_explanation_text.setFont(font)

        layout.addWidget(summary_explanation_text)

        summary = self.data_processing_dialog.model.statsmodel_result_by_ratio.summary()
        summary_iterable = str(summary).splitlines()

        for line in summary_iterable:
            print(line)
            h_layout = QHBoxLayout()
            for item in line.split():
                q_item = QLabel(item)
                q_item.setFont(font)
                h_layout.addWidget(q_item)
            h_layout.setAlignment(Qt.AlignCenter)
            layout.addLayout(h_layout)

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
        predicted_values = self.data_processing_dialog.model.statsmodel_result_by_ratio.predict()
        true_values = self.data_processing_dialog.model.primary_rm_deltas_by_ratio[self.ratio]
        residuals = true_values - predicted_values

        self.residuals_axis.plot(predicted_values, residuals, ls="", marker="o")

        self.residuals_axis.set_xlabel("Fitted values")
        self.residuals_axis.set_ylabel("Residuals")

        plt.tight_layout()
