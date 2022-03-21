from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QFileDialog

from src.utils.make_csv_file import write_csv_output, get_output_file
from src.view.cycle_data_dialog import CycleDataDialog


class CorrectedDataWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog

        self.basic_data_table = self._create_basic_table()

        self.data_processing_dialog.model.signals.replotAndTabulateRecalculatedData.connect(self.update_basic_table)

        layout = QHBoxLayout()

        lhs_layout = self._create_lhs_layout()

        layout.addLayout(lhs_layout)

        self.setLayout(layout)

    def _create_lhs_layout(self):
        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self._populate_basic_table()

        data_output_button = QPushButton("Export corrected data")
        data_output_button.clicked.connect(self.on_data_output_button_pushed)

        analytical_conditions_button = QPushButton("Export analytical conditions file")
        analytical_conditions_button.clicked.connect(self.on_analytical_conditions_button_pushed)

        button_layout.addWidget(data_output_button)
        button_layout.addWidget(analytical_conditions_button)

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
        output_file_name = get_output_file("corrected_data")

        method = self.data_processing_dialog.method

        column_headers = ["Sample name", "Spot excluded"]
        for ratio in method.ratios:
            column_headers.append("corrected " + ratio.delta_name)
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio_uncertainty_name)
            column_headers.append("uncorrected " + ratio.delta_name)
            column_headers.append(ratio_uncertainty_name)
            column_headers.append("uncorrected " + ratio.name)
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.data_processing_dialog.samples:
            for spot in sample.spots:
                if spot.is_flagged:
                    spot_excluded = "x"
                else:
                    spot_excluded = ""
                row = [str(sample.name + "-" + spot.id), spot_excluded]

                for ratio in method.ratios:
                    [delta, delta_uncertainty] = spot.alpha_corrected_data[ratio.delta_name]
                    [uncorrected_delta, uncorrected_delta_uncertainty] = spot.not_corrected_deltas[ratio.delta_name]
                    [uncorrected_ratio, uncorrected_ratio_uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
                    row.append(delta)
                    row.append(delta_uncertainty)
                    row.append(uncorrected_delta)
                    row.append(uncorrected_delta_uncertainty)
                    row.append(uncorrected_ratio)
                    row.append(uncorrected_ratio_uncertainty)

                row.append(spot.dtfa_x)
                row.append(spot.dtfa_y)
                row.append(format(spot.secondary_ion_yield, ".5f"))
                row.append(spot.distance_from_mount_centre)

                rows.append(row)
        if output_file_name:
            write_csv_output(headers=column_headers, rows=rows, output_file=output_file_name)

    def on_analytical_conditions_button_pushed(self):
        output_file_name = get_output_file("analytical_data")
        column_headers = []
        rows = [row for row in self.data_processing_dialog.model.analytical_condition_data if row]

        if output_file_name:
            write_csv_output(headers=column_headers, rows=rows, output_file=output_file_name)

    #############
    ### Table ###
    #############

    def _create_basic_table(self):

        method = self.data_processing_dialog.method

        number_of_columns = 5 + (2 * len(method.ratios))
        number_of_rows = 0

        column_headers = ["Sample name"]
        for ratio in method.ratios:
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
                        delta, delta_uncertainty = spot.alpha_corrected_data[ratio.delta_name]
                        delta_text = format(delta, ".3f")
                    else:
                        delta_text = "No delta calculated"
                    delta_item = QTableWidgetItem(delta_text)
                    delta_item.setFont(font)
                    self.basic_data_table.setItem(i, j, delta_item)
                    j += 1
                    if ratio in spot.standard_ratios:
                        delta, delta_uncertainty = spot.alpha_corrected_data[ratio.delta_name]
                        delta_uncertainty_text = format(delta_uncertainty, ".4f")
                    else:
                        delta_uncertainty_text = "No delta calculated"
                    delta_uncertainty_item = QTableWidgetItem(delta_uncertainty_text)
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

    def update_basic_table(self):
        self.basic_data_table.clearContents()
        self._populate_basic_table()
