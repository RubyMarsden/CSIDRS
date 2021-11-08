import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget

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
        layout.addLayout(self._create_left_widget())
        layout.addLayout(self._create_right_widget())

        self.sample_tree.tree.currentItemChanged.connect(lambda x, y: self.plot_spot_graph(
                                                            self.sample_tree.tree.currentItem().spot,
                                                            self.axes
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

        return layout

    def _create_title_bar(self):
        layout = QHBoxLayout()
        title = QLabel("hi")
        layout.addWidget(title)
        return layout

    def _create_cycle_data_graphs(self):
        graph = QWidget()
        layout = QVBoxLayout()

        fig = plt.figure()
        self.axes = plt.axes()

        graph_widget, self.canvas = gui_utils.create_figure_widget(fig, self)

        layout.addWidget(graph_widget)

        graph.setLayout(layout)

        return graph


    def plot_spot_graph(self, spot, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        print("hi")

        for mass_peak in spot.mass_peaks.values():
            xs = range(0, len(mass_peak[0].detector_corrected_cps_data))
            ys = mass_peak[0].detector_corrected_cps_data
            print(xs, ys)

        axis.plot(xs, ys)
        axis.set_xlabel("Relative spot time (s)")
        axis.set_ylabel("SBM (cps)")
        plt.tight_layout()
        plt.show()

