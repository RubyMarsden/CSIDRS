from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QFrame
from matplotlib import pyplot as plt

from utils import gui_utils
from view.ratio_box_widget import RatioBoxWidget


class ResidualsDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Residuals and statsmodels statistics summary")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog

        self.ratio = data_processing_dialog.get_current_ratio()
        # Create the ratio selection button here - because the button must exist before ratio can change.
        self.ratio_selection_widget = self._create_ratio_selection_widget()

        self.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.ratio_selection_widget)

        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self._create_graph_widget(), 4)
        lower_layout.addWidget(self._create_regression_results_summary_widget(), 6)

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

        summary_explanation_text = QLabel("The following parameters come from the python statsmodels package. They "
                                          "are listed here for completeness, however it is understood that users will "
                                          "not always be able to disregard linear drift if these parameters are not "
                                          "as expected as the model is simplified for usability.")
        summary_explanation_text.setWordWrap(True)
        summary_explanation_text.setFont(font)

        layout.addWidget(summary_explanation_text)

        summary = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].summary()
        summary_iterable = str(summary).splitlines()
        self.summary_line_labels = []
        for line in summary_iterable:
            if line and line[0] == "=":
                q_item = QFrame()
                q_item.setFrameShape(QFrame.HLine)
                q_item.setLineWidth(1)
                q_item.setMinimumWidth(150)
            else:
                q_item = QLabel(line)
                q_item.setFont(font)
                q_item.setAlignment(Qt.AlignCenter)

            self.summary_line_labels.append(q_item)
            layout.addWidget(q_item)

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
        predicted_values = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].predict()
        true_values = self.data_processing_dialog.model.primary_rm_deltas_by_ratio[self.ratio]
        residuals = true_values - predicted_values

        self.residuals_axis.plot(predicted_values, residuals, ls="", marker="o")

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
        self.reallocate_label_text()

    def reallocate_label_text(self):
        summary = self.data_processing_dialog.model.statsmodel_result_by_ratio[self.ratio].summary()
        summary_iterable = str(summary).splitlines()

        for (q_widget, line) in zip(self.summary_line_labels, summary_iterable):
            if line and line[0] != "=":
                q_widget.setText(line)
