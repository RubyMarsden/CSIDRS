import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QTreeWidgetItem, QTreeWidget
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

from src.utils import gui_utils
from src.view.cycle_tree_widget import CycleTreeWidget
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
        self.cycle_tree = CycleTreeWidget()

        self.ratio = self.data_processing_dialog.method_dictionary["ratios"][0]

        layout = QHBoxLayout()
        right_widget = self._create_right_widget()
        layout.addLayout(self._create_left_widget())
        layout.addLayout(right_widget)

        self.sample_tree.tree.currentItemChanged.connect(lambda x, y: self.update_graphs(
            self.sample_tree.current_spot(),
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

        layout.addWidget(self.cycle_tree)
        self.cycle_tree.set_cycles(self.sample_tree.current_spot(), self.ratio)

        # TODO show Matthew how broken I can make things
        # for sample in self.samples:
        #     for spot in sample.spots:
        #         spot_item = self.sample_tree.tree.currentItem()
        #         for i, value in enumerate(spot.raw_isotope_ratios[self.data_processing_dialog.method_dictionary["ratios"][0]]):
        #             item = QTreeWidgetItem(spot_item)
        #             item.setText(0, str(i))
        #             item.is_sample = False
        #             item.is_spot = False
        #             spot_item.addChild(item)
        #             item.is_flagged = False


        return layout

    def _create_title_bar(self):
        layout = QHBoxLayout()
        title = QLabel("Ratios and cps per cycle")
        layout.addWidget(title)
        return layout



    ###############
    ### Actions ###
    ###############

    def update_graphs(self, spot, ratio):
        self.counts_axis.clear()
        self.counts_axis2.clear()
        self.ratios_axis.clear()
        if spot is not None:
            self.create_counts_plot(spot, self.counts_axis, self.counts_axis2, ratio)
            self.create_ratio_plot(spot, self.ratios_axis, ratio)

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
        self.counts_axis2 = self.counts_axis.twinx()
        self.ratios_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self.create_counts_plot(self.sample_tree.current_spot(), self.counts_axis, self.counts_axis2, self.ratio)
        self.create_ratio_plot(self.sample_tree.current_spot(), self.ratios_axis, self.ratio)

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph

    def create_counts_plot(self, spot, axis, axis2, ratio):
        plt.cla()
        axis.clear()
        axis2.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        y1s = spot.mass_peaks[ratio.numerator].detector_corrected_cps_data
        y2s = spot.mass_peaks[ratio.denominator].detector_corrected_cps_data

        x1s = range(1, 1 + len(y1s))
        x2s = range(1, 1 + len(y2s))

        axis.plot(x1s, y1s, ls="", marker="x", color="red")
        axis2.plot(x2s, y2s, ls="", marker="+", color="black")

        axis.set_xlabel("Cycle")
        axis.set_ylabel("Counts per second")
        plt.xticks(x1s, x1s)
        axis.set_xticks(x1s)
        plt.setp(axis.get_xticklabels(), visible=True)
        plt.autoscale(enable=True, axis='y')
        plt.tight_layout()

    def create_ratio_plot(self, spot, ratio_axis, ratio):
        # TODO - add method to this section
        ratio_axis.clear()
        ratio_axis.spines['top'].set_visible(False)
        ratio_axis.spines['right'].set_visible(False)

        ratio_axis.set_ylabel(ratio.name)
        ys = spot.raw_isotope_ratios[ratio]
        xs = list(range(1, 1 + len(ys)))

        for x, y in zip(xs, ys):
            if y in spot.outliers_removed_from_raw_data[ratio.name]:
                ratio_axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="navy")
            else:
                ratio_axis.plot(x, y, ls="", marker="o", color="navy")
        ratio_axis.set_xlabel("Cycle")

        mean, two_st_error = spot.mean_two_st_error_isotope_ratios[ratio]
        plt.axhline(y=mean)

        (outlier_minimum, outlier_maximum) = spot.outlier_bounds[ratio.name]
        outlier_rectangle = Rectangle((0, outlier_minimum), len(xs)+1, outlier_maximum - outlier_minimum)

        outlier_rectangle.set_color("lightblue")

        ratio_axis.add_patch(outlier_rectangle)

        st_error_rectangle = Rectangle((0, mean - two_st_error), len(xs) + 1, 2 * two_st_error)
        st_error_rectangle.set_color("cornflowerblue")

        ratio_axis.add_patch(st_error_rectangle)

        plt.xticks(xs, xs)
        plt.tight_layout()
