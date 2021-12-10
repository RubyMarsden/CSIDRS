import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle

from src.utils import gui_utils
from src.view.ratio_box_widget import RatioBoxWidget

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt


class QualityControlWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.ratio = self.data_processing_dialog.method.ratios[0]
        self.samples = data_processing_dialog.samples

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)

        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_graph_tabs)

        layout = QVBoxLayout()

        graph_widget = self._create_graph_tab_widget(self.ratio)
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)

        self.ratio_radiobox_widget.set_ratio(self.ratio)

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(graph_widget)

        self.setLayout(layout)

    def _create_graph_tab_widget(self, ratio):
        # self.fig = plt.figure()
        #
        # self.delta_vs_time_axis = self.fig.add_subplot()

        delta_vs_time_graph_widget = self._create_delta_vs_time_graph_widget()
        x_y_position_graph_widget = self._create_x_y_position_graph_widget()
        delta_vs_secondary_ion_yield_graph_widget = self._create_delta_vs_secondary_ion_yield_graph_widget()
        delta_vs_distance_mount_centre_graph_widget = self._create_delta_vs_distance_from_mount_centre_graph_widget()
        delta_vs_dtfa_x_graph_widget = self._create_delta_vs_dtfa_x_graph_widget()
        delta_vs_dtfa_y_graph_widget = self._create_delta_vs_dtfa_y_graph_widget()

        graph_tab_widget = QTabWidget()
        graph_tab_widget.addTab(delta_vs_time_graph_widget, "Time")
        graph_tab_widget.addTab(x_y_position_graph_widget, "x and y position")
        graph_tab_widget.addTab(delta_vs_secondary_ion_yield_graph_widget, "Secondary ion yield")
        graph_tab_widget.addTab(delta_vs_distance_mount_centre_graph_widget, "Distance to mount centre")
        graph_tab_widget.addTab(delta_vs_dtfa_x_graph_widget, "dtfa-x")
        graph_tab_widget.addTab(delta_vs_dtfa_y_graph_widget, "dtfa-y")

        return graph_tab_widget

    def _create_delta_vs_time_graph_widget(self):
        fig = plt.figure()

        self.delta_vs_time_axis = fig.add_subplot()
        graph_widget, self.time_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_x_y_position_graph_widget(self):
        fig = plt.figure()

        self.x_and_y_position_axis = fig.add_subplot()
        graph_widget, self.x_y_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_delta_vs_secondary_ion_yield_graph_widget(self):
        fig = plt.figure()

        self.delta_vs_secondary_ion_yield_axis = fig.add_subplot()
        graph_widget, self.secondary_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_delta_vs_distance_from_mount_centre_graph_widget(self):
        fig = plt.figure()

        self.delta_vs_distance_from_mount_centre_axis = fig.add_subplot()
        graph_widget, self.distance_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_delta_vs_dtfa_x_graph_widget(self):
        fig = plt.figure()

        self.delta_vs_dtfa_x_axis = fig.add_subplot()
        graph_widget, self.dtfa_x_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_delta_vs_dtfa_y_graph_widget(self):
        fig = plt.figure()

        self.delta_vs_dtfa_y_axis = fig.add_subplot()
        graph_widget, self.dtfa_y_canvas = gui_utils.create_figure_widget(fig, self)

        return graph_widget

    def _create_delta_vs_time_graph(self, ratio):
        self.delta_vs_time_axis.clear()

        self.delta_vs_time_axis.set_title(ratio.delta_name + " against time.")

        self.delta_vs_time_axis.spines['top'].set_visible(False)
        self.delta_vs_time_axis.spines['right'].set_visible(False)
        for sample in self.samples:
            xs = [spot.datetime for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            self.delta_vs_time_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)

        self.delta_vs_time_axis.set_xlabel("Time")
        self.delta_vs_time_axis.set_ylabel(ratio.delta_name)
        self.delta_vs_time_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()

    def _create_x_y_position_graph(self):
        self.x_and_y_position_axis.clear()
        self.x_and_y_position_axis.spines['top'].set_visible(False)
        self.x_and_y_position_axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [int(spot.x_position) for spot in sample.spots]
            ys = [int(spot.y_position) for spot in sample.spots]
            self.x_and_y_position_axis.plot(xs, ys, marker="o", ls="", markersize=3, color=sample.colour)

        circle = Circle((0, 0), 9000)
        circle.set_color("lightgoldenrodyellow")

        range_of_radians = np.linspace(0, 2 * np.pi, 100)
        self.x_and_y_position_axis.plot(7000 * np.cos(range_of_radians), 7000 * np.sin(range_of_radians), marker="", ls="-", color="r")
        self.x_and_y_position_axis.plot(5000 * np.cos(range_of_radians), 5000 * np.sin(range_of_radians), marker="", ls="--", color="r")

        self.x_and_y_position_axis.add_patch(circle)

        self.x_and_y_position_axis.set_xlabel("X position")
        self.x_and_y_position_axis.set_ylabel("Y position")
        self.x_and_y_position_axis.set(xlim=(-9000, 9000), ylim=(-9000, 9000))
        plt.axis('scaled')
        plt.tight_layout()

    def _create_delta_vs_secondary_ion_yield_graph(self, ratio):
        self.delta_vs_secondary_ion_yield_axis.clear()
        self.delta_vs_secondary_ion_yield_axis.set_title(ratio.delta_name + " against secondary ion yields.")
        self.delta_vs_secondary_ion_yield_axis.spines['top'].set_visible(False)
        self.delta_vs_secondary_ion_yield_axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.secondary_ion_yield for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            self.delta_vs_secondary_ion_yield_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        self.delta_vs_secondary_ion_yield_axis.set_xlabel("Secondary ion yield")
        self.delta_vs_secondary_ion_yield_axis.set_ylabel(ratio.delta_name)
        plt.tight_layout()

    def _create_delta_vs_distance_from_mount_centre_graph(self, ratio):
        self.delta_vs_distance_from_mount_centre_axis.clear()
        self.delta_vs_distance_from_mount_centre_axis.set_title(ratio.delta_name + " against distance from mount centre.")
        self.delta_vs_distance_from_mount_centre_axis.spines['top'].set_visible(False)
        self.delta_vs_distance_from_mount_centre_axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.distance_from_mount_centre for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            self.delta_vs_distance_from_mount_centre_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        self.delta_vs_distance_from_mount_centre_axis.set_xlabel("Distance from mount centre")
        self.delta_vs_distance_from_mount_centre_axis.set_ylabel(ratio.delta_name)

        plt.tight_layout()

    def _create_delta_vs_dtfa_x_graph(self, ratio):
        self.delta_vs_dtfa_x_axis.clear()
        self.delta_vs_dtfa_x_axis.set_title(ratio.delta_name + " against dtfa-x.")
        self.delta_vs_dtfa_x_axis.spines['top'].set_visible(False)
        self.delta_vs_dtfa_x_axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.dtfa_x for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            self.delta_vs_dtfa_x_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        self.delta_vs_dtfa_x_axis.set_xlabel("dtfa-x")
        self.delta_vs_dtfa_x_axis.set_ylabel(ratio.delta_name)

        plt.tight_layout()

    def _create_delta_vs_dtfa_y_graph(self, ratio):
        self.delta_vs_dtfa_y_axis.clear()
        self.delta_vs_dtfa_y_axis.set_title(ratio.delta_name + " against dtfa-y.")
        self.delta_vs_dtfa_y_axis.spines['top'].set_visible(False)
        self.delta_vs_dtfa_y_axis.spines['right'].set_visible(False)

        total_xs = []
        for sample in self.samples:
            xs = [spot.dtfa_y for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]
            total_xs.extend(xs)

            self.delta_vs_dtfa_y_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)

        x_minimum = min(total_xs) - 2
        x_maximum = max(total_xs) + 2

        self.delta_vs_dtfa_y_axis.set_xlabel("dtfa-y")
        self.delta_vs_dtfa_y_axis.set_ylabel(ratio.delta_name)
        self.delta_vs_dtfa_y_axis.set(xlim=(x_minimum, x_maximum))
        # plt.xlim([x_minimum, x_maximum])

        plt.tight_layout()

    ###############
    ### Actions ###
    ###############

    def change_ratio(self, ratio):
        self.ratio = ratio
        self.update_graph_tabs()

    def update_graph_tabs(self):
        self._create_delta_vs_time_graph(self.ratio)
        self._create_x_y_position_graph()
        self._create_delta_vs_secondary_ion_yield_graph(self.ratio)
        self._create_delta_vs_distance_from_mount_centre_graph(self.ratio)
        self._create_delta_vs_dtfa_x_graph(self.ratio)
        self._create_delta_vs_dtfa_y_graph(self.ratio)

        self.time_canvas.draw()
        self.x_y_canvas.draw()
        self.secondary_canvas.draw()
        self.distance_canvas.draw()
        self.dtfa_x_canvas.draw()
        self.dtfa_y_canvas.draw()
