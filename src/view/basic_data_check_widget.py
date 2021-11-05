import matplotlib
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QLabel, QCheckBox
from matplotlib.gridspec import GridSpec

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

        data_output_button = QPushButton("Extract data")
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
        dialog = CycleDataDialog()
        result = dialog.exec()

    def on_data_output_button_pushed(self):
        print("Create a csv")
        return

    ################
    ### Plotting ###
    ################

    def _create_graphs_to_check_data(self):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.spot_invisible_grid_spec = GridSpec(1, 1)
        self.spot_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.x_y_pos_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self.create_all_samples_basic_data_plot(self.data_processing_dialog.samples, self.x_y_pos_axis)

        widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return widget

    def create_all_samples_basic_data_plot(self, samples, axis):
        axis.clear()
        xs = []
        ys = []
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in samples:
            for spot in sample.spots:
                xs.append(int(spot.x_position))
                ys.append(int(spot.y_position))


        axis.plot(xs, ys, marker="o", ls="")
        axis.set_xlabel("X position")
        axis.set_ylabel("Y position")
        plt.axis('scaled')
        plt.tight_layout()
