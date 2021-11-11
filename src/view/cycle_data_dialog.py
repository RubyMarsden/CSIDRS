import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget
from matplotlib.gridspec import GridSpec

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
        if spot is None:
            self.counts_axis.clear()
            self.ratios_axis.clear()
        else:
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
        # self.spot_invisible_grid_spec = GridSpec(1, 1)
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
        xs = []
        ys = []
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for mass_peak in spot.mass_peaks.values():
            xs = range(0, len(mass_peak.detector_corrected_cps_data))
            ys = mass_peak.detector_corrected_cps_data

            axis.plot(xs, ys, ls="", marker="x")
        axis.set_xlabel("Cycle")
        axis.set_ylabel("Counts per second")
        plt.tight_layout()


    def create_ratio_plot(self, spot, axis):
        # TODO - add method to this section
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        y1s = spot.mass_peaks["18O"][0].detector_corrected_cps_data
        y2s = spot.mass_peaks["16O"][0].detector_corrected_cps_data

        ys = []
        for y1 in y1s:
            y = y1/y2s[y1s.index(y1)]
            ys.append(y)

        xs = range(0, len(ys))

        axis.plot(xs, ys, ls="", marker="o")
        axis.set_xlabel("Cycle")
        axis.set_ylabel("Ratio")
        plt.tight_layout()
