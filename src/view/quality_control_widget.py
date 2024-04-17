import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from matplotlib.patches import Circle

from controllers.signals import signals
from utils import gui_utils

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt


class QualityControlWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.model = data_processing_dialog.model

        self.data_processing_dialog.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)
        self.data_processing_dialog.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_changed)
        signals.dataRecalculated.connect(self.on_data_recalculated)

        layout = QVBoxLayout()

        graph_widget = self._create_graph_tab_widget()
        layout.addWidget(graph_widget)

        self.setLayout(layout)

    def _create_graph_tab_widget(self):
        corrected_value_vs_time_graph_widget = self._create_corrected_value_vs_time_graph_widget()
        x_y_position_graph_widget = self._create_x_y_position_graph_widget()
        corrected_value_vs_secondary_ion_yield_graph_widget = self._create_corrected_value_vs_secondary_ion_yield_graph_widget()
        corrected_value_vs_distance_mount_centre_graph_widget = self._create_corrected_value_vs_distance_from_mount_centre_graph_widget()
        corrected_value_vs_dtfa_x_graph_widget = self._create_corrected_value_vs_dtfa_x_graph_widget()
        corrected_value_vs_dtfa_y_graph_widget = self._create_corrected_value_vs_dtfa_y_graph_widget()

        graph_tab_widget = QTabWidget()
        graph_tab_widget.addTab(corrected_value_vs_time_graph_widget, "Time")
        graph_tab_widget.addTab(x_y_position_graph_widget, "x and y position")
        graph_tab_widget.addTab(corrected_value_vs_secondary_ion_yield_graph_widget, "Secondary ion yield")
        graph_tab_widget.addTab(corrected_value_vs_distance_mount_centre_graph_widget, "Distance to mount centre")
        graph_tab_widget.addTab(corrected_value_vs_dtfa_x_graph_widget, "dtfa-x")
        graph_tab_widget.addTab(corrected_value_vs_dtfa_y_graph_widget, "dtfa-y")

        return graph_tab_widget

    def _create_corrected_value_vs_time_graph_widget(self):
        self.corrected_value_vs_time_fig = plt.figure()

        self.corrected_value_vs_time_axis = self.corrected_value_vs_time_fig.add_subplot()
        graph_widget, self.time_canvas = gui_utils.create_figure_widget(self.corrected_value_vs_time_fig, self)

        return graph_widget

    def _create_x_y_position_graph_widget(self):
        self.x_y_position_fig = plt.figure()

        self.x_and_y_position_axis = self.x_y_position_fig.add_subplot()
        graph_widget, self.x_y_canvas = gui_utils.create_figure_widget(self.x_y_position_fig, self)

        return graph_widget

    def _create_corrected_value_vs_secondary_ion_yield_graph_widget(self):
        self.corrected_value_vs_secondary_ion_fig = plt.figure()

        self.corrected_value_vs_secondary_ion_yield_axis = self.corrected_value_vs_secondary_ion_fig.add_subplot()
        graph_widget, self.secondary_canvas = gui_utils.create_figure_widget(self.corrected_value_vs_secondary_ion_fig,
                                                                             self)

        return graph_widget

    def _create_corrected_value_vs_distance_from_mount_centre_graph_widget(self):
        self.corrected_value_vs_distance_fig = plt.figure()

        self.corrected_value_vs_distance_from_mount_centre_axis = self.corrected_value_vs_distance_fig.add_subplot()
        graph_widget, self.distance_canvas = gui_utils.create_figure_widget(self.corrected_value_vs_distance_fig, self)

        return graph_widget

    def _create_corrected_value_vs_dtfa_x_graph_widget(self):
        self.corrected_values_vs_dtfa_x_fig = plt.figure()

        self.corrected_value_vs_dtfa_x_axis = self.corrected_values_vs_dtfa_x_fig.add_subplot()
        graph_widget, self.dtfa_x_canvas = gui_utils.create_figure_widget(self.corrected_values_vs_dtfa_x_fig, self)

        return graph_widget

    def _create_corrected_value_vs_dtfa_y_graph_widget(self):
        self.corrected_value_vs_dtfa_y_fig = plt.figure()

        self.corrected_value_vs_dtfa_y_axis = self.corrected_value_vs_dtfa_y_fig.add_subplot()
        graph_widget, self.dtfa_y_canvas = gui_utils.create_figure_widget(self.corrected_value_vs_dtfa_y_fig, self)

        return graph_widget

    def _create_corrected_value_vs_time_graph(self, ratio):
        self.corrected_value_vs_time_axis.clear()

        corrected_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
        self.corrected_value_vs_time_axis.set_title(corrected_value_name + " against time, 2sig uncertainty.")

        self.corrected_value_vs_time_axis.spines['top'].set_visible(False)
        self.corrected_value_vs_time_axis.spines['right'].set_visible(False)
        for sample in self.model.get_samples():
            xs = [spot.datetime for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                ys.append(np.mean(spot.alpha_corrected_data[ratio]))
                dys.append((2 * np.std(spot.alpha_corrected_data[ratio])))

            self.corrected_value_vs_time_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)

        self.corrected_value_vs_time_axis.set_xlabel("Time")
        self.corrected_value_vs_time_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        self.corrected_value_vs_time_axis.set_ylabel(corrected_value_name)

        self.corrected_value_vs_time_fig.tight_layout()

    def _create_x_y_position_graph(self):
        self.x_and_y_position_axis.clear()
        self.x_and_y_position_axis.spines['top'].set_visible(False)
        self.x_and_y_position_axis.spines['right'].set_visible(False)

        for sample in self.model.get_samples():
            xs = [int(spot.x_position) for spot in sample.spots]
            ys = [int(spot.y_position) for spot in sample.spots]
            self.x_and_y_position_axis.plot(xs, ys, marker="o", ls="", markersize=3, color=sample.colour)

        circle = Circle((0, 0), 9000)
        circle.set_color("lightgoldenrodyellow")

        range_of_radians = np.linspace(0, 2 * np.pi, 100)
        self.x_and_y_position_axis.plot(7000 * np.cos(range_of_radians), 7000 * np.sin(range_of_radians), marker="",
                                        ls="-", color="r")
        self.x_and_y_position_axis.plot(5000 * np.cos(range_of_radians), 5000 * np.sin(range_of_radians), marker="",
                                        ls="--", color="r")

        self.x_and_y_position_axis.add_patch(circle)

        self.x_and_y_position_axis.set_xlabel("X position")
        self.x_and_y_position_axis.set_ylabel("Y position")
        self.x_and_y_position_axis.set(xlim=(-9000, 9000), ylim=(-9000, 9000))
        self.x_and_y_position_axis.set_aspect('equal')
        self.x_y_position_fig.tight_layout()

    def _create_corrected_value_vs_secondary_ion_yield_graph(self, ratio):
        self.corrected_value_vs_secondary_ion_yield_axis.clear()
        corrected_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
        self.corrected_value_vs_secondary_ion_yield_axis.set_title(
            corrected_value_name + " against secondary ion yields, 2sig uncertainty.")
        self.corrected_value_vs_secondary_ion_yield_axis.spines['top'].set_visible(False)
        self.corrected_value_vs_secondary_ion_yield_axis.spines['right'].set_visible(False)

        for sample in self.model.get_samples():
            xs = [spot.secondary_ion_yield for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                ys.append(np.mean(spot.alpha_corrected_data[ratio]))
                dys.append((2 * np.std(spot.alpha_corrected_data[ratio])))


            self.corrected_value_vs_secondary_ion_yield_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o",
                                                                      color=sample.colour)
        self.corrected_value_vs_secondary_ion_yield_axis.set_xlabel("Secondary ion yield")
        self.corrected_value_vs_secondary_ion_yield_axis.set_ylabel(corrected_value_name)
        self.corrected_value_vs_secondary_ion_fig.tight_layout()

    def _create_corrected_value_vs_distance_from_mount_centre_graph(self, ratio):
        self.corrected_value_vs_distance_from_mount_centre_axis.clear()
        corrected_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
        self.corrected_value_vs_distance_from_mount_centre_axis.set_title(
            corrected_value_name + " against distance from mount centre, 2sig uncertainty.")
        self.corrected_value_vs_distance_from_mount_centre_axis.spines['top'].set_visible(False)
        self.corrected_value_vs_distance_from_mount_centre_axis.spines['right'].set_visible(False)

        for sample in self.model.get_samples():
            xs = [spot.distance_from_mount_centre for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                ys.append(np.mean(spot.alpha_corrected_data[ratio]))
                dys.append((2 * np.std(spot.alpha_corrected_data[ratio])))

            self.corrected_value_vs_distance_from_mount_centre_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o",
                                                                             color=sample.colour)
        self.corrected_value_vs_distance_from_mount_centre_axis.set_xlabel("Distance from mount centre")
        self.corrected_value_vs_distance_from_mount_centre_axis.set_ylabel(corrected_value_name)

        self.corrected_value_vs_distance_fig.tight_layout()

    def _create_corrected_value_vs_dtfa_x_graph(self, ratio):
        self.corrected_value_vs_dtfa_x_axis.clear()
        corrected_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
        self.corrected_value_vs_dtfa_x_axis.set_title(corrected_value_name + " against dtfa-x, 2sig uncertainty.")
        self.corrected_value_vs_dtfa_x_axis.spines['top'].set_visible(False)
        self.corrected_value_vs_dtfa_x_axis.spines['right'].set_visible(False)

        for sample in self.model.get_samples():
            xs = [spot.dtfa_x for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                ys.append(np.mean(spot.alpha_corrected_data[ratio]))
                dys.append((2 * np.std(spot.alpha_corrected_data[ratio])))

            self.corrected_value_vs_dtfa_x_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        self.corrected_value_vs_dtfa_x_axis.set_xlabel("dtfa-x")

        self.corrected_values_vs_dtfa_x_fig.tight_layout()
        self.corrected_value_vs_dtfa_x_axis.set_ylabel(corrected_value_name)

    def _create_corrected_value_vs_dtfa_y_graph(self, ratio):
        self.corrected_value_vs_dtfa_y_axis.clear()
        corrected_value_name = ratio.delta_name() if ratio.has_delta else ratio.name()
        self.corrected_value_vs_dtfa_y_axis.set_title(corrected_value_name + " against dtfa-y, 2sig uncertainty.")
        self.corrected_value_vs_dtfa_y_axis.spines['top'].set_visible(False)
        self.corrected_value_vs_dtfa_y_axis.spines['right'].set_visible(False)

        total_xs = []
        for sample in self.model.get_samples():
            xs = [spot.dtfa_y for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                ys.append(np.mean(spot.alpha_corrected_data[ratio]))
                dys.append((2 * np.std(spot.alpha_corrected_data[ratio])))

            total_xs.extend(xs)

            self.corrected_value_vs_dtfa_y_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)

        x_minimum = min(total_xs) - 2
        x_maximum = max(total_xs) + 2

        self.corrected_value_vs_dtfa_y_axis.set_xlabel("dtfa-y")
        self.corrected_value_vs_dtfa_y_axis.set_ylabel(corrected_value_name)
        self.corrected_value_vs_dtfa_y_axis.set(xlim=(x_minimum, x_maximum))

        self.corrected_value_vs_dtfa_y_fig.tight_layout()

    ###############
    ### Actions ###
    ###############
    def on_sample_tree_item_changed(self, current_item, previous_tree_item):
        self.highlight_selected_ratio_data_point(current_item, previous_tree_item)

    def on_ratio_changed(self, ratio):
        self.update_graph_tabs(ratio)

    def on_data_recalculated(self):
        ratio = self.data_processing_dialog.get_current_ratio()
        self.update_graph_tabs(ratio)

    def update_graph_tabs(self, ratio):
        self._create_corrected_value_vs_time_graph(ratio)
        self._create_x_y_position_graph()
        self._create_corrected_value_vs_secondary_ion_yield_graph(ratio)
        self._create_corrected_value_vs_distance_from_mount_centre_graph(ratio)
        self._create_corrected_value_vs_dtfa_x_graph(ratio)
        self._create_corrected_value_vs_dtfa_y_graph(ratio)

        self.time_canvas.draw()
        self.x_y_canvas.draw()
        self.secondary_canvas.draw()
        self.distance_canvas.draw()
        self.dtfa_x_canvas.draw()
        self.dtfa_y_canvas.draw()

    def highlight_selected_ratio_data_point(self, current_item, previous_tree_item):
        return
