import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle

from utils.make_csv_file import write_csv_output, get_output_file
from view.ratio_box_widget import RatioBoxWidget

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt

from utils.gui_utils import create_figure_widget
from view.cycle_data_dialog import CycleDataDialog


class BasicDataCheckWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog

        self.ratio = self.data_processing_dialog.method.ratios[0]
        self.samples = data_processing_dialog.samples

        self.data_processing_dialog.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_changed)
        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)

        self.graph_widget = self._create_graphs_to_check_data()
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)

        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=False)

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

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(self.graph_widget)

        return layout

    ###############
    ### Actions ###
    ###############
    def on_sample_tree_item_changed(self, current_item, previous_tree_item):
        self.highlight_selected_ratio_data_point(current_item, previous_tree_item)

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog(self.data_processing_dialog)
        result = dialog.exec()

    def change_ratio(self, ratio):
        self.ratio = ratio
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=True)
        self.update_graphs()

    def update_graphs(self):
        self.create_raw_delta_time_plot(self.ratio)
        self.canvas.draw()

    def on_data_output_button_pushed(self):
        method = self.data_processing_dialog.method

        output_file_name = get_output_file("raw_data")

        column_headers = ["Sample name"]
        for ratio in method.ratios:
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio.name())
            column_headers.append(ratio_uncertainty_name)
            if ratio.has_delta:
                column_headers.append(ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.data_processing_dialog.samples:
            for spot in sample.spots:
                row = [str(sample.name + " " + spot.id)]

                for ratio in method.ratios:
                    ratio_value, ratio_uncertainty = spot.mean_two_st_error_isotope_ratios[ratio]
                    row.append(ratio_value)
                    row.append(ratio_uncertainty)
                    if ratio.has_delta:
                        delta, delta_uncertainty = spot.not_corrected_deltas[ratio]
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
            self.create_raw_delta_time_plot()
            self.create_ion_distance_data_plot()
        else:
            current_spot = current_item.spot
            if previous_tree_item is None or previous_tree_item.is_sample:
                self.create_raw_delta_time_plot()
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
                    self.raw_delta_time_axis.plot(x.datetime, y, ls="", marker="o", markersize=4, color="yellow")

                if x == previous_spot:
                    self.raw_delta_time_axis.plot(x.datetime, y, ls="", marker="o", markersize=4, color=sample.colour)

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
            if ratio.has_delta:
                column_headers.append(ratio.delta_name())
            else:
                column_headers.append(ratio.name())
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        for sample in self.data_processing_dialog.samples:
            for _spot in sample.spots:
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
        row_number = 0
        for sample in self.data_processing_dialog.samples:
            background_colour = sample.q_colour
            for spot in sample.spots:
                row_items = []
                row_items.append(str(sample.name + " " + spot.id))

                for ratio in method.ratios:
                    if ratio.has_delta:
                        value, uncertainty = spot.not_corrected_deltas[ratio]
                        value_format = ".3f"
                        uncertainty_format = ".4f"
                    else:
                        value, uncertainty = spot.mean_two_st_error_isotope_ratios[ratio]
                        value_format = ".5f"
                        uncertainty_format = ".6f"

                    row_items.append(format(value, value_format))
                    row_items.append(format(uncertainty, uncertainty_format))

                row_items.append(str(spot.dtfa_x))
                row_items.append(str(spot.dtfa_y))
                row_items.append(format(spot.secondary_ion_yield, ".3f"))
                row_items.append(str(round(spot.distance_from_mount_centre)))

                for column_number, value in enumerate(row_items):
                    item = QTableWidgetItem(value)
                    item.setFont(font)
                    if column_number == 0:
                        item.setBackground(background_colour)
                    elif spot.is_flagged:
                        item.setBackground(QColor("red"))

                    self.basic_data_table.setItem(row_number, column_number, item)

                row_number += 1

        self.basic_data_table.resizeColumnsToContents()

    ################
    ### Plotting ###
    ################

    def _create_graphs_to_check_data(self):
        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1, height_ratios=[1, 2])
        self.raw_delta_time_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.x_y_pos_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        self.create_raw_delta_time_plot(self.ratio)
        self.create_all_samples_x_y_positions_plot(self.data_processing_dialog.samples, self.x_y_pos_axis)

        widget, self.canvas = create_figure_widget(self.fig, self)

        return widget

    def create_raw_delta_time_plot(self, ratio):
        self.raw_delta_time_axis.clear()

        self.raw_delta_time_axis.spines['top'].set_visible(False)
        self.raw_delta_time_axis.spines['right'].set_visible(False)
        for sample in self.samples:
            xs = [spot.datetime for spot in sample.spots]
            ys = []
            dys = []
            for spot in sample.spots:
                if ratio.has_delta:
                    self.raw_delta_time_axis.set_title("Raw " + ratio.delta_name() + " against time.")
                    ys.append(spot.not_corrected_deltas[ratio][0])
                    dys.append(spot.not_corrected_deltas[ratio][1])

                    self.raw_delta_time_axis.set_ylabel(ratio.delta_name())

                else:
                    self.raw_delta_time_axis.set_title("Raw " + ratio.name() + " against time.")
                    ys.append(spot.mean_two_st_error_isotope_ratios[ratio][0])
                    dys.append(spot.mean_two_st_error_isotope_ratios[ratio][1])

                    self.raw_delta_time_axis.set_ylabel(ratio.name())
                    self.raw_delta_time_axis.set_ylabel(ratio.name())

            self.raw_delta_time_axis.errorbar(xs, ys, yerr=dys, ls="", marker="o", markersize=4, color=sample.colour)

        self.raw_delta_time_axis.set_xlabel("Time")
        self.raw_delta_time_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

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
