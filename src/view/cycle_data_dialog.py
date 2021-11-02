import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget

from src.utils import gui_utils

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class CycleDataDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle("Cycle data")
        self.setMinimumWidth(450)

        layout = QHBoxLayout()
        layout.addLayout(self._create_left_widget())
        self.setLayout(layout)

    def _create_left_widget(self):
        layout = QVBoxLayout()
        layout.addLayout(self._create_title_bar())
        layout.addWidget(self._create_cycle_data_graphs())

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


