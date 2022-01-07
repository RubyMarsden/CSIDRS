from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QWidget, QLabel, QVBoxLayout
from matplotlib import pyplot as plt

from src.utils import gui_utils


class ResidualsDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Residuals and statsmodels statistics summary")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog

        layout = QHBoxLayout()
        layout.addWidget(self._create_graph_widget())
        layout.addWidget(self._create_regression_results_summary_widget())

        self._create_residuals_graph()

        self.setLayout(layout)

    def _create_graph_widget(self):
        self.fig = plt.figure()

        self.residuals_axis = plt.axes()

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

    def _create_regression_results_summary_widget(self):
        regression_results_widget = QWidget()
        layout = QVBoxLayout()
        summary = self.data_processing_dialog.model.statsmodel_result.summary()
        summary_iterable = str(summary).splitlines()
        for line in summary_iterable:
            print(line)
            h_layout = QHBoxLayout()
            for item in line.split():
                q_item = QLabel(item)
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
        predicted_values = self.data_processing_dialog.model.statsmodel_result.predict()
        true_values = self.data_processing_dialog.model.primary_deltas
        residuals = true_values - predicted_values

        self.residuals_axis.plot(predicted_values, residuals, ls="", marker="o")

        self.residuals_axis.set_xlabel("Fitted values")
        self.residuals_axis.set_ylabel("Residuals")

        plt.tight_layout()
