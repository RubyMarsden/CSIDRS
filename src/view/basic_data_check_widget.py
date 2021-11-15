import matplotlib
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QLabel, QCheckBox
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle
import matplotlib.dates as mdates

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt

from src.utils import gui_utils
from src.view.cycle_data_dialog import CycleDataDialog


class BasicDataCheckWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog

        layout = QHBoxLayout()

        lhs_layout = self._create_lhs_layout()
        rhs_layout = self._create_rhs_layout()

        layout.addLayout(lhs_layout)
        layout.addLayout(rhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        table = QTableWidget()

        cycle_data_button = QPushButton("Operators only")
        cycle_data_button.clicked.connect(self.on_cycle_data_button_pushed)
        button_layout.addWidget(cycle_data_button)

        data_output_button = QPushButton("Extract raw data")
        data_output_button.clicked.connect(self.on_data_output_button_pushed)
        button_layout.addWidget(data_output_button)

        layout.addWidget(table)
        layout.addLayout(button_layout)

        return layout

    def _create_rhs_layout(self):
        layout = QVBoxLayout()
        graphs = self._create_graphs_to_check_data()
        checkbox = QCheckBox("Ok")
        layout.addWidget(graphs)
        layout.addWidget(checkbox, alignment=Qt.AlignRight)

        return layout

    ###############
    ### Actions ###
    ###############

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog(self.data_processing_dialog.samples)
        result = dialog.exec()

    def on_data_output_button_pushed(self):
        print("Create a csv")
        return

    ################
    ### Plotting ###
    ################

    def _create_graphs_to_check_data(self):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(3, 1)
        # self.spot_invisible_grid_spec = GridSpec(1, 1)
        self.ion_yield_time_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.ion_yield_distance_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])
        self.x_y_pos_axis = self.fig.add_subplot(self.spot_visible_grid_spec[2])

        self.create_ion_yield_time_plot(self.data_processing_dialog.samples, self.ion_yield_time_axis)
        self.create_ion_distance_data_plot(self.data_processing_dialog.samples, self.ion_yield_distance_axis)
        self.create_all_samples_x_y_positions_plot(self.data_processing_dialog.samples, self.x_y_pos_axis)

        widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return widget

    def create_ion_yield_time_plot(self, samples, axis):
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in samples:
            xs = []
            ys = []
            colour = sample.colour
            for spot in sample.spots:
                xs.append(spot.datetime)
                ys.append(spot.secondary_ion_yield)

            axis.plot(xs, ys, marker="o", ls="", color=colour)

        axis.set_xlabel("Time")
        plt.setp(axis.get_xticklabels(), rotation=30, horizontalalignment='right')
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        axis.set_ylabel("Relative secondary \n ion yield")
        plt.tight_layout()

    def create_ion_distance_data_plot(self, samples, axis):
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in samples:
            xs = []
            ys = []
            for spot in sample.spots:
                xs.append(spot.distance_from_mount_centre)
                ys.append(spot.secondary_ion_yield)

            axis.plot(xs, ys, marker="o", ls="", color=sample.colour)
        axis.set_xlabel("Distance from centre of mount")
        axis.set_ylabel("Relative secondary \n ion yield")
        plt.tight_layout()

    def create_all_samples_x_y_positions_plot(self, samples, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in samples:
            xs = []
            ys = []
            for spot in sample.spots:
                xs.append(int(spot.x_position))
                ys.append(int(spot.y_position))

            axis.plot(xs, ys, marker="o", ls="", markersize=2, color=sample.colour)

        circle = Circle((0, 0), 9000)
        circle.set_color("lightgoldenrodyellow")

        range_of_radians = np.linspace(0, 2 * np.pi, 100)
        axis.plot(7000 * np.cos(range_of_radians), 7000 * np.sin(range_of_radians), marker="", ls="-", color="r")
        axis.plot(5000 * np.cos(range_of_radians), 5000 * np.sin(range_of_radians), marker="", ls="--", color="r")

        axis.add_patch(circle)

        axis.set_xlabel("X position")
        axis.set_ylabel("Y position")
        axis.set(xlim=(-9000, 9000), ylim=(-9000, 9000))
        plt.axis('scaled')
        plt.tight_layout()
