from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from matplotlib import pyplot as plt

from src.model.isotopes import Isotope
from src.utils import gui_utils


class SulphurCAPWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method.ratios[0]
        self.samples = data_processing_dialog.samples
        self.method = data_processing_dialog.method

        layout = QVBoxLayout()

        graph_widget = self._create_graph_tab_widget()
        layout.addWidget(graph_widget)

        self.update_graph_tabs()

        self.setLayout(layout)

    def _create_graph_tab_widget(self):
        delta_four_vs_delta_three_graph_widget = self._create_delta_four_vs_delta_three_graph_widget()
        delta_four_vs_delta_six_graph_widget = self._create_delta_four_vs_delta_six_graph_widget()
        cap_three_vs_delta_four_graph_widget = self._create_cap_three_vs_delta_four_graph_widget()
        cap_three_vs_cap_six_graph_widget = self._create_cap_three_vs_cap_six_graph_widget()

        graph_tab_widget = QTabWidget()
        graph_tab_widget.addTab(delta_four_vs_delta_three_graph_widget, "delta33 vs delta34")
        graph_tab_widget.addTab(cap_three_vs_delta_four_graph_widget, "Cap33 vs delta34")
        if Isotope.S36 in self.data_processing_dialog.method.isotopes:
            graph_tab_widget.addTab(delta_four_vs_delta_six_graph_widget, "delta36 vs delta34")
            graph_tab_widget.addTab(cap_three_vs_cap_six_graph_widget, "Cap36 vs Cap33")

        return graph_tab_widget

    def _create_delta_four_vs_delta_three_graph_widget(self):
        self.delta_four_vs_delta_three_fig = plt.figure()

        self.delta_four_vs_delta_three_axis = self.delta_four_vs_delta_three_fig.add_subplot()
        graph_widget, self.delta_four_vs_delta_three_canvas = gui_utils.create_figure_widget(
            self.delta_four_vs_delta_three_fig, self)

        return graph_widget

    def _create_delta_four_vs_delta_six_graph_widget(self):
        self.delta_four_vs_delta_six_fig = plt.figure()

        self.delta_four_vs_delta_six_axis = self.delta_four_vs_delta_six_fig.add_subplot()
        graph_widget, self.delta_four_vs_delta_six_canvas = gui_utils.create_figure_widget(
            self.delta_four_vs_delta_six_fig, self)

        return graph_widget

    def _create_cap_three_vs_delta_four_graph_widget(self):
        self.cap_three_vs_delta_four_fig = plt.figure()

        self.cap_three_vs_delta_four_axis = self.cap_three_vs_delta_four_fig.add_subplot()
        graph_widget, self.cap_three_vs_delta_four_canvas = gui_utils.create_figure_widget(
            self.cap_three_vs_delta_four_fig, self)

        return graph_widget

    def _create_cap_three_vs_cap_six_graph_widget(self):
        self.cap_three_vs_cap_six_fig = plt.figure()

        self.cap_three_vs_cap_six_axis = self.cap_three_vs_cap_six_fig.add_subplot()
        graph_widget, self.cap_three_vs_cap_six_canvas = gui_utils.create_figure_widget(
            self.cap_three_vs_cap_six_fig, self)

        return graph_widget

################
### PLOTTING ###
################

    def _create_delta_four_vs_delta_three_graph(self):
        self.delta_four_vs_delta_three_axis.clear()
        self.delta_four_vs_delta_three_axis.set_title("delta33 vs delta34")
        self.delta_four_vs_delta_three_axis.spines['top'].set_visible(False)
        self.delta_four_vs_delta_three_axis.spines['right'].set_visible(False)

        for sample in self.samples:
            delta_three = [spot.drift_corrected_deltas[self.method.ratios[0].delta_name][0] for spot in sample.spots]
            delta_three_errors = [spot.drift_corrected_deltas[self.method.ratios[0].delta_name][1] for spot in sample.spots]
            delta_four = [spot.drift_corrected_deltas[self.method.ratios[1].delta_name][0] for spot in sample.spots]
            delta_four_errors = [spot.drift_corrected_deltas[self.method.ratios[1].delta_name][1] for spot in sample.spots]

            self.delta_four_vs_delta_three_axis.errorbar(delta_four, delta_three,xerr=delta_four_errors, yerr=delta_three_errors, ls="", marker="o", color=sample.colour)

    def _create_delta_four_vs_delta_six_graph(self):
        return

    def _create_cap_three_vs_delta_four_graph(self):
        return

    def _create_cap_three_vs_cap_six_graph(self):
        return

    def update_graph_tabs(self):
        self._create_delta_four_vs_delta_three_graph()

        self.delta_four_vs_delta_three_canvas.draw()