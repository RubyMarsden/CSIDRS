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

        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_graphs)

        layout = QVBoxLayout()

        graph_widget = self._create_graph_tab_widget(self.ratio)
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)

        self.ratio_radiobox_widget.set_ratio(self.ratio)

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(graph_widget)

        self.setLayout(layout)

    def _create_graph_widget(self, ratio):
        graph = QWidget()
        layout = QVBoxLayout()

        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(3, 2)
        self.delta_vs_time_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0, 0])
        self.x_and_y_position_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0, 1])
        self.delta_vs_secondary_ion_yield_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1, 0])
        self.delta_vs_distance_from_mount_centre_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1, 1])
        self.delta_vs_dtfa_x_axis = self.fig.add_subplot(self.spot_visible_grid_spec[2, 0])
        self.delta_vs_dtfa_y_axis = self.fig.add_subplot(self.spot_visible_grid_spec[2, 1])

        self._create_delta_vs_time_graph(self.delta_vs_time_axis, ratio)
        self._create_x_y_position_graph(self.x_and_y_position_axis)
        self._create_delta_vs_secondary_ion_yield_graph(self.delta_vs_secondary_ion_yield_axis, ratio)
        self._create_delta_vs_distance_from_mount_centre_graph(self.delta_vs_distance_from_mount_centre_axis, ratio)
        self._create_delta_vs_dtfa_x_graph(self.delta_vs_dtfa_x_axis, ratio)
        self._create_delta_vs_dtfa_y_graph(self.delta_vs_dtfa_y_axis, ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph

    def _create_delta_vs_time_graph(self, axis, ratio):
        axis.clear()

        axis.set_title(ratio.delta_name + " against time.")

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in self.samples:
            xs = [spot.datetime for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)

        axis.set_xlabel("Time")
        axis.set_ylabel(ratio.delta_name)
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')

        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        plt.tight_layout()

    def _create_x_y_position_graph(self, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [int(spot.x_position) for spot in sample.spots]
            ys = [int(spot.y_position) for spot in sample.spots]
            axis.plot(xs, ys, marker="o", ls="", markersize=1, color=sample.colour)

        circle = Circle((0, 0), 9000)
        circle.set_color("lightgoldenrodyellow")

        range_of_radians = np.linspace(0, 2 * np.pi, 100)
        axis.plot(7000 * np.cos(range_of_radians), 7000 * np.sin(range_of_radians), marker="", ls="-", color="r")
        axis.plot(5000 * np.cos(range_of_radians), 5000 * np.sin(range_of_radians), marker="", ls="--", color="r")

        axis.add_patch(circle)

        axis.set_xlabel("X position")
        axis.set_ylabel("Y position")
        axis.set(xlim=(-9000, 9000), ylim=(-9000, 9000))
        plt.axis('equal')
        plt.tight_layout()

    def _create_delta_vs_secondary_ion_yield_graph(self, axis, ratio):
        axis.clear()
        axis.set_title(ratio.delta_name + " against secondary ion yields.")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.secondary_ion_yield for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("Secondary ion yield")
        axis.set_ylabel(ratio.delta_name)
        plt.tight_layout()

    def _create_delta_vs_distance_from_mount_centre_graph(self, axis, ratio):
        axis.clear()
        axis.set_title(ratio.delta_name + " against distance from mount centre.")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.distance_from_mount_centre for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("Distance from mount centre")
        axis.set_ylabel(ratio.delta_name)
        plt.tight_layout()

    def _create_delta_vs_dtfa_x_graph(self, axis, ratio):
        axis.clear()
        axis.set_title(ratio.delta_name + " against dtfa-x.")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.dtfa_x for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("dtfa-x")
        axis.set_ylabel(ratio.delta_name)
        plt.tight_layout()

    def _create_delta_vs_dtfa_y_graph(self, axis, ratio):
        axis.clear()
        axis.set_title(ratio.delta_name + " against dtfa-y.")
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in self.samples:
            xs = [spot.dtfa_y for spot in sample.spots]
            ys = [spot.alpha_corrected_data[ratio.delta_name][0] for spot in sample.spots]
            dys = [spot.alpha_corrected_data[ratio.delta_name][1] for spot in sample.spots]

            axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", color=sample.colour)
        axis.set_xlabel("dtfa-y")
        axis.set_ylabel(ratio.delta_name)
        plt.tight_layout()

    ###############
    ### Actions ###
    ###############

    def change_ratio(self, ratio):
        self.ratio = ratio
        print(ratio)
        self.update_graphs()

    def update_graphs(self):
        self.delta_vs_time_axis.clear()
        self.delta_vs_secondary_ion_yield_axis.clear()
        self.delta_vs_distance_from_mount_centre_axis.clear()
        self.delta_vs_dtfa_x_axis.clear()
        self.delta_vs_dtfa_y_axis.clear()
        self._create_delta_vs_time_graph(self.delta_vs_time_axis, self.ratio)
        self._create_delta_vs_secondary_ion_yield_graph(self.delta_vs_secondary_ion_yield_axis, self.ratio)
        self._create_delta_vs_distance_from_mount_centre_graph(self.delta_vs_distance_from_mount_centre_axis, self.ratio)
        self._create_delta_vs_dtfa_x_graph(self.delta_vs_dtfa_x_axis, self.ratio)
        self._create_delta_vs_dtfa_y_graph(self.delta_vs_dtfa_y_axis, self.ratio)

        self.canvas.draw()
