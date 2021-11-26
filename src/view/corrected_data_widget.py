import matplotlib
import matplotlib.dates as mdates
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QCheckBox, \
    QTableWidgetItem, QHeaderView
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle

matplotlib.use('QT5Agg')
from matplotlib import pyplot as plt

from src.utils import gui_utils
from src.view.cycle_data_dialog import CycleDataDialog


class CorrectedDataWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog

        layout = QHBoxLayout()

        lhs_layout = self._create_lhs_layout()

        layout.addLayout(lhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.basic_data_table = self._create_basic_table()
        self._populate_basic_table()

        data_output_button = QPushButton("Export corrected data")
        data_output_button.clicked.connect(self.on_data_output_button_pushed)
        button_layout.addWidget(data_output_button)

        layout.addWidget(self.basic_data_table)
        layout.addLayout(button_layout)

        return layout

    ###############
    ### Actions ###
    ###############

    def on_cycle_data_button_pushed(self):
        dialog = CycleDataDialog(self.data_processing_dialog)
        result = dialog.exec()

    def on_data_output_button_pushed(self):
        print("Create a csv")

    #############
    ### Table ###
    #############

    def _create_basic_table(self):

        method = self.data_processing_dialog.method_dictionary

        number_of_columns = 5 + (2 * method["number_of_ratios"])
        number_of_rows = 0

        column_headers = ["Sample name"]
        for ratio in method["ratios"]:
            column_headers.append("Corrected " + ratio.delta_name)
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
        method = self.data_processing_dialog.method_dictionary

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

                for ratio in method["ratios"]:
                    j += 1
                    [delta, delta_uncertainty] = spot.alpha_corrected_data[ratio.delta_name]
                    delta_item = QTableWidgetItem(format(delta, ".3f"))
                    delta_item.setFont(font)
                    self.basic_data_table.setItem(i, j, delta_item)
                    j += 1
                    delta_uncertainty_item = QTableWidgetItem(format(delta_uncertainty, ".4f"))
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
