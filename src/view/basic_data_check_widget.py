import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle

from src.utils.make_csv_file import write_csv_output, get_output_file

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt

from src.utils import gui_utils
from src.view.cycle_data_dialog import CycleDataDialog


class BasicDataCheckWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog
        self.data_processing_dialog.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_changed)

        layout = QHBoxLayout()

        lhs_layout = self._create_lhs_layout()
        rhs_layout = self._create_rhs_layout()

        layout.addLayout(lhs_layout)
        layout.addLayout(rhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.basic_data_table = self._create_basic_table()
        self._populate_basic_table()

        cycle_data_button = QPushButton("Operators only")
        cycle_data_button.clicked.connect(self.on_cycle_data_button_pushed)
        button_layout.addWidget(cycle_data_button)

        data_output_button = QPushButton("Extract raw data")
        data_output_button.clicked.connect(self.on_data_output_button_pushed)
        button_layout.addWidget(data_output_button)

        layout.addWidget(self.basic_data_table)
        layout.addLayout(button_layout)

        return layout

    def _create_rhs_layout(self):
        layout = QVBoxLayout()
        graphs = self._create_graphs_to_check_data()
        layout.addWidget(graphs)

        return layout

    ###############
    ### Actions ###
    ###############
    def on_sample_tree_item_changed(self, current_item, previous_tree_item):
        self.highlight_selected_ratio_data_point(current_item, previous_tree_item)

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog(self.data_processing_dialog)
        result = dialog.exec()

    def on_data_output_button_pushed(self):
        method = self.data_processing_dialog.method

        output_file_name = get_output_file("raw_data")

        column_headers = ["Sample name"]
        for ratio in method.ratios:
            column_headers.append(ratio.delta_name)
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.data_processing_dialog.samples:
            for spot in sample.spots:
                row = [str(sample.name + " " + spot.id)]

                for ratio in method.ratios:
                    [delta, delta_uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                    row.append(delta)
                    row.append(delta_uncertainty)

                row.append(spot.dtfa_x)
                row.append(spot.dtfa_y)
                row.append(format(spot.secondary_ion_yield, ".5f"))
                row.append(spot.distance_from_mount_centre)

                rows.append(row)

        if output_file_name:
            write_csv_output(headers=column_headers, rows=rows, output_file=output_file_name)

    def highlight_selected_ratio_data_point(self, current_item, previous_tree_item):
        if current_item is None or current_item.is_sample:
            self.create_ion_yield_time_plot()
            self.create_ion_distance_data_plot()
        else:
            current_spot = current_item.spot
            if previous_tree_item is None or previous_tree_item.is_sample:
                self.create_ion_yield_time_plot()
                self.create_ion_distance_data_plot()
                previous_spot = None
            else:
                previous_spot = previous_tree_item.spot
            xs = []
            ys = []
            for sample in self.data_processing_dialog.samples:
                for spot in sample.spots:
                    ys.append(spot.secondary_ion_yield)
                    xs.append(spot)

            for x, y in zip(xs, ys):
                sample = self.data_processing_dialog.model.samples_by_name[x.sample_name]
                if x == current_spot:
                    self.ion_yield_distance_axis.plot(x.distance_from_mount_centre, y, ls="", marker="o", markersize=4,
                                                      color="yellow")
                    self.ion_yield_time_axis.plot(x.datetime, y, ls="", marker="o", markersize=4, color="yellow")

                if x == previous_spot:
                    self.ion_yield_distance_axis.plot(x.distance_from_mount_centre, y, ls="", marker="o", markersize=4,
                                                      color=sample.colour)
                    self.ion_yield_time_axis.plot(x.datetime, y, ls="", marker="o", markersize=4, color=sample.colour)

        self.canvas.draw()

    #############
    ### Table ###
    #############

    def _create_basic_table(self):

        method = self.data_processing_dialog.method

        number_of_columns = 5 + (2 * len(method.ratios))
        number_of_rows = 0

        column_headers = ["Sample name"]
        for ratio in method.ratios:
            column_headers.append(ratio.delta_name)
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        for sample in self.data_processing_dialog.samples:
            for spot in sample.spots:
                number_of_rows += 1

        table = QTableWidget()
        table.verticalHeader().setVisible(False)
        table.setColumnCount(number_of_columns)
        table.setRowCount(number_of_rows)

        table.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter | Qt.Alignment(QtCore.Qt.TextWordWrap))
        table.horizontalHeader().setStyleSheet("QHeaderView { font-size: 9pt; }")
        # table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # table.horizontalHeader().setMinimumHeight(40)
        table.setHorizontalHeaderLabels(column_headers)

        table.setEditTriggers(QTableWidget.NoEditTriggers)

        return table

    def _populate_basic_table(self):
        method = self.data_processing_dialog.method

        font_family = self.basic_data_table.font().family()
        font = QFont(font_family, 9)
        i = 0
        for sample in self.data_processing_dialog.samples:
            background_colour = sample.q_colour
            for spot in sample.spots:
                j = 0
                name_item = QTableWidgetItem(str(sample.name + " " + spot.id))
                name_item.setBackground(background_colour)
                name_item.setFont(font)
                self.basic_data_table.setItem(i, j, name_item)

                for ratio in method.ratios:
                    j += 1
                    if ratio in spot.standard_ratios:
                        delta, delta_uncertainty = spot.not_corrected_deltas[ratio.delta_name]
                        delta_item = QTableWidgetItem(format(delta, ".3f"))
                    else:
                        delta_item = QTableWidgetItem("No delta calculated")
                    delta_item.setFont(font)
                    self.basic_data_table.setItem(i, j, delta_item)
                    j += 1
                    if ratio in spot.standard_ratios:
                        delta, delta_uncertainty = spot.not_corrected_deltas[ratio.delta_name]
                        delta_uncertainty_item = QTableWidgetItem(format(delta_uncertainty, ".4f"))
                    else:
                        delta_uncertainty_item = QTableWidgetItem("No delta calculated")
                    delta_uncertainty_item.setFont(font)
                    self.basic_data_table.setItem(i, j, delta_uncertainty_item)
                    if spot.is_flagged:
                        delta_item.setBackground(QColor("red"))
                        delta_uncertainty_item.setBackground(QColor("red"))

                dtfa_x_item = QTableWidgetItem(str(spot.dtfa_x))
                dtfa_y_item = QTableWidgetItem(str(spot.dtfa_y))
                relative_ion_yield_item = QTableWidgetItem(format(spot.secondary_ion_yield, ".3f"))
                distance_to_mount_centre_item = QTableWidgetItem(str(round(spot.distance_from_mount_centre)))

                for item in [dtfa_x_item, dtfa_y_item, relative_ion_yield_item, distance_to_mount_centre_item]:
                    item.setFont(font)
                    if spot.is_flagged:
                        item.setBackground(QColor("red"))

                self.basic_data_table.setItem(i, j + 1, dtfa_x_item)
                self.basic_data_table.setItem(i, j + 2, dtfa_y_item)
                self.basic_data_table.setItem(i, j + 3, relative_ion_yield_item)
                self.basic_data_table.setItem(i, j + 4, distance_to_mount_centre_item)
                i += 1
        self.basic_data_table.resizeColumnsToContents()

    ################
    ### Plotting ###
    ################

    def _create_graphs_to_check_data(self):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(3, 1, height_ratios=[1, 1, 2])
        self.ion_yield_time_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.ion_yield_distance_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])
        self.x_y_pos_axis = self.fig.add_subplot(self.spot_visible_grid_spec[2])

        self.create_ion_yield_time_plot()
        self.create_ion_distance_data_plot()
        self.create_all_samples_x_y_positions_plot(self.data_processing_dialog.samples, self.x_y_pos_axis)

        widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return widget

    def create_ion_yield_time_plot(self):
        axis = self.ion_yield_time_axis
        samples = self.data_processing_dialog.samples
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in samples:
            colour = sample.colour
            xs = [spot.datetime for spot in sample.spots]
            ys = [spot.secondary_ion_yield for spot in sample.spots]

            axis.plot(xs, ys, marker="o", ls="", markersize=4, color=colour)

        axis.set_xlabel("Time")
        for x_tick_label in axis.get_xticklabels():
            x_tick_label.set_rotation(30)
            x_tick_label.set_horizontalalignment('right')
        axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

        axis.set_ylabel("Relative secondary \n ion yield")
        self.fig.tight_layout()

    def create_ion_distance_data_plot(self):
        axis = self.ion_yield_distance_axis
        samples = self.data_processing_dialog.samples
        axis.clear()

        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)
        for sample in samples:
            xs = [spot.distance_from_mount_centre for spot in sample.spots]
            ys = [spot.secondary_ion_yield for spot in sample.spots]
            axis.plot(xs, ys, marker="o", ls="", markersize=4, color=sample.colour)

        axis.set_xlabel("Distance from centre of mount")
        axis.set_ylabel("Relative secondary \n ion yield")
        self.fig.tight_layout()

    def create_all_samples_x_y_positions_plot(self, samples, axis):
        axis.clear()
        axis.spines['top'].set_visible(False)
        axis.spines['right'].set_visible(False)

        for sample in samples:
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
        axis.set_aspect('equal')
        self.fig.tight_layout()
