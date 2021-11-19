import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

from src.utils import gui_utils
from src.view.sample_tree import SampleTreeWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class CycleDataDialog(QDialog):
    def __init__(self, samples):
        QDialog.__init__(self)
        self.setWindowTitle("Cycle data")
        self.setMinimumWidth(450)

        self.samples = samples
        self.sample_tree = SampleTreeWidget()

        layout = QHBoxLayout()
        right_widget = self._create_right_widget()
        layout.addLayout(self._create_left_widget())
        layout.addLayout(right_widget)

        self.sample_tree.tree.currentItemChanged.connect(lambda x, y: self.update_graphs(
            self.sample_tree.current_spot(),
            self.counts_axis,
            self.ratios_axis
        )
                                                         )

        self.setLayout(layout)

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addLayout(self._create_title_bar())
        layout.addWidget(self._create_cycle_data_graphs())

        return layout

    def _create_right_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        self.sample_tree.set_samples(self.samples)
        self.sample_tree.select_first_spot()

        return layout

    def _create_title_bar(self):
        layout = QHBoxLayout()
        title = QLabel("Ratios and cps per cycle")
        layout.addWidget(title)
        return layout

    ###############
    ### Actions ###
    ###############

    def update_graphs(self, spot, counts_axis, ratios_axis):
        self.counts_axis.clear()
        self.ratios_axis.clear()
        if spot is not None:
            self.create_counts_plot(spot, counts_axis)
            self.create_ratio_plot(spot, ratios_axis)

        self.canvas.draw()

    ################
    ### Plotting ###
    ################

    def _create_cycle_data_graphs(self):
        graph = QWidget()
        layout = QVBoxLayout()

        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.counts_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.ratios_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self.create_counts_plot(self.sample_tree.current_spot(), self.counts_axis)
        self.create_ratio_plot(self.sample_tree.current_spot(), self.ratios_axis)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph

    def create_counts_plot(self, spot, axis):
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for mass_peak in spot.mass_peaks.values():
            ys = mass_peak.detector_corrected_cps_data
            xs = range(1, 1 + len(ys))
            axis.plot(xs, ys, ls="", marker="x")

        axis.set_xlabel("Cycle")
        axis.set_ylabel("Counts per second")
        plt.xticks(xs, xs)
        axis.set_xticks(xs)
        plt.setp(axis.get_xticklabels(), visible=True)
        plt.tight_layout()

    def create_ratio_plot(self, spot, axis):
        # TODO - add method to this section
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        axis.set_ylabel(spot.raw_isotope_ratios.keys())
        ys = list(spot.raw_isotope_ratios.values())[0]
        xs = list(range(1, 1 + len(ys)))

        removed_xs = []
        removed_ys = []

        for x, y in zip(xs, ys):
            if y in spot.outliers_removed_from_raw_data[list(spot.raw_isotope_ratios.keys())[0]]:
                axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="navy")
            else:
                axis.plot(x, y, ls="", marker="o", color="navy")
        axis.set_xlabel("Cycle")

        mean, st_error = spot.mean_st_error_isotope_ratios[list(spot.raw_isotope_ratios.keys())[0]]
        plt.axhline(y=mean)

        (outlier_minimum, outlier_maximum) = spot.outlier_bounds[list(spot.raw_isotope_ratios.keys())[0]]
        outlier_rectangle = Rectangle((0, outlier_minimum), len(xs)+1, outlier_maximum - outlier_minimum)

        outlier_rectangle.set_color("lightblue")

        axis.add_patch(outlier_rectangle)

        st_error_rectangle = Rectangle((0, mean - 2* st_error), len(xs) + 1, 4*st_error)
        st_error_rectangle.set_color("cornflowerblue")

        axis.add_patch(st_error_rectangle)

        plt.xticks(xs, xs)
        plt.tight_layout()
