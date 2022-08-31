import math

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from matplotlib import pyplot as plt

from model.isotopes import Isotope
from utils import gui_utils

from src.model.settings.methods_from_isotopes import S34_S32


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

    def _create_delta_graph(self, axis, ratio_x_index, ratio_y_index, MDF_factor):
        ratio_y = self.method.ratios[ratio_y_index]
        ratio_x = self.method.ratios[ratio_x_index]
        axis.clear()
        axis.set_title(ratio_y.delta_name + " vs " + ratio_x.delta_name)
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        axis.set_xlabel(ratio_x.delta_name)
        axis.set_ylabel(ratio_y.delta_name)

        list_for_finding_minimum_and_maximum_x_values = [0]
        list_for_finding_minimum_and_maximum_y_values = [0]

        for sample in self.samples:
            delta_y_value = [spot.alpha_corrected_data[ratio_y.delta_name][0] for spot in
                             sample.spots]
            delta_y_errors = [spot.alpha_corrected_data[ratio_y.delta_name][1] for spot in
                              sample.spots]
            delta_x_value = [spot.alpha_corrected_data[ratio_x.delta_name][0] for spot in
                             sample.spots]
            delta_x_errors = [spot.alpha_corrected_data[ratio_x.delta_name][1] for spot in
                              sample.spots]
            list_for_finding_minimum_and_maximum_y_values.extend(delta_y_value)
            list_for_finding_minimum_and_maximum_x_values.extend(delta_x_value)
            axis.errorbar(delta_x_value, delta_y_value, xerr=delta_x_errors,
                          yerr=delta_y_errors, ls="", marker="o",
                          color=sample.colour, label=sample.name)

        list_for_finding_minimum_and_maximum_x_values.append(
            min(list_for_finding_minimum_and_maximum_y_values) / MDF_factor)
        list_for_finding_minimum_and_maximum_x_values.append(
            max(list_for_finding_minimum_and_maximum_y_values) / MDF_factor)
        minimum = min(list_for_finding_minimum_and_maximum_x_values)
        maximum = max(list_for_finding_minimum_and_maximum_x_values)
        round_down_minimum = math.floor(minimum)
        round_up_maximum = math.ceil(maximum)
        xs = range(round_down_minimum, round_up_maximum + 1, 1)
        ys = [MDF_factor * x for x in xs]

        axis.plot(xs, ys, marker="", ls="-", color='lightgray', label='MDF')
        axis.legend()

    def _create_cap_three_vs_delta_four_graph(self, axis):
        axis.clear()
        axis.set_title("Cap S33 vs delta S34")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xlabel("delta S34")
        axis.set_ylabel("Cap S33")

        for sample in self.samples:
            xs = [spot.alpha_corrected_data[S34_S32.delta_name][0] for spot in sample.spots]
            x_errors = [spot.alpha_corrected_data[S34_S32.delta_name][1] for spot in sample.spots]
            ys = [spot.cap_data_S33[0] for spot in sample.spots]
            y_errors = [spot.cap_data_S33[1] for spot in sample.spots]

            axis.errorbar(x=xs, xerr=x_errors, y=ys, yerr=y_errors, ls="", marker="o", color=sample.colour,
                          label=sample.name)

        axis.legend()

    def _create_cap_three_vs_cap_six_graph(self, axis):
        axis.clear()
        axis.set_title("Cap S33 vs Cap S36")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        axis.set_xlabel("Cap S33")
        axis.set_ylabel("Cap S36")

        for sample in self.samples:
            xs = [spot.cap_data_S33[0] for spot in sample.spots]
            x_errors = [spot.cap_data_S33[1] for spot in sample.spots]
            ys = [spot.cap_data_S36[0] for spot in sample.spots]
            y_errors = [spot.cap_data_S36[1] for spot in sample.spots]

            axis.errorbar(x=xs, xerr=x_errors, y=ys, yerr=y_errors, ls="", marker="o", color=sample.colour,
                          label=sample.name)

        axis.legend()

    def update_graph_tabs(self):
        self._create_delta_graph(self.delta_four_vs_delta_three_axis, 1, 0, 0.515)
        self._create_delta_graph(self.delta_four_vs_delta_six_axis, 1, 2, 1.91)
        self._create_cap_three_vs_delta_four_graph(self.cap_three_vs_delta_four_axis)
        self._create_cap_three_vs_cap_six_graph(self.cap_three_vs_cap_six_axis)

        self.delta_four_vs_delta_three_canvas.draw()
        self.delta_four_vs_delta_six_canvas.draw()
        self.cap_three_vs_delta_four_canvas.draw()
        self.cap_three_vs_cap_six_canvas.draw()
