import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

from src.utils import gui_utils
from src.view.sample_tree import SampleTreeWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class CycleDataDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Cycle data")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog

        self.samples = self.data_processing_dialog.samples
        self.sample_tree = SampleTreeWidget()

        self.ratio = self.data_processing_dialog.method_dictionary["ratios"][0]

        layout = QHBoxLayout()
        right_widget = self._create_right_widget()
        layout.addLayout(self._create_left_widget())
        layout.addLayout(right_widget)

        self.sample_tree.tree.currentItemChanged.connect(lambda x, y: self.update_graphs(
            self.sample_tree.current_spot(),
            self.counts_axis,
            self.ratios_axis,
            self.ratio
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

    def update_graphs(self, spot, counts_axis, ratios_axis, ratio):
        self.counts_axis.clear()
        self.ratios_axis.clear()
        if spot is not None:
            self.create_counts_plot(spot, counts_axis, ratio)
            self.create_ratio_plot(spot, ratios_axis, ratio)

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

        self.create_counts_plot(self.sample_tree.current_spot(), self.counts_axis, self.ratio)
        self.create_ratio_plot(self.sample_tree.current_spot(), self.ratios_axis, self.ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph

    def create_counts_plot(self, spot, axis, ratio):
        #axis2 = axis.twinx()
        axis.clear()
        #axis2.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        y1s = spot.mass_peaks[ratio.numerator].detector_corrected_cps_data
        y2s = spot.mass_peaks[ratio.denominator].detector_corrected_cps_data

        x1s = range(1, 1 + len(y1s))
        x2s = range(1, 1 + len(y2s))

        axis.plot(x1s, y1s, ls="", marker="x")
        axis.plot(x2s, y2s, ls="", marker="+")

        axis.set_xlabel("Cycle")
        axis.set_ylabel("Counts per second")
        plt.xticks(x1s, x1s)
        axis.set_xticks(x1s)
        plt.setp(axis.get_xticklabels(), visible=True)
        plt.autoscale(enable=True, axis='y')
        plt.tight_layout()

    def create_ratio_plot(self, spot, axis, ratio):
        # TODO - add method to this section
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        axis.set_ylabel(ratio.name)
        ys = list(spot.raw_isotope_ratios.values())[0]
        xs = list(range(1, 1 + len(ys)))

        for x, y in zip(xs, ys):
            if y in spot.outliers_removed_from_raw_data[ratio.name]:
                axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="navy")
            else:
                axis.plot(x, y, ls="", marker="o", color="navy")
        axis.set_xlabel("Cycle")

        mean, two_st_error = spot.mean_two_st_error_isotope_ratios[ratio]
        plt.axhline(y=mean)

        (outlier_minimum, outlier_maximum) = spot.outlier_bounds[ratio.name]
        outlier_rectangle = Rectangle((0, outlier_minimum), len(xs)+1, outlier_maximum - outlier_minimum)

        outlier_rectangle.set_color("lightblue")

        axis.add_patch(outlier_rectangle)

        st_error_rectangle = Rectangle((0, mean - two_st_error), len(xs) + 1, 2 * two_st_error)
        st_error_rectangle.set_color("cornflowerblue")

        axis.add_patch(st_error_rectangle)

        plt.xticks(xs, xs)
        plt.tight_layout()
