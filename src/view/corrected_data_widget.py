from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QFileDialog

from utils.make_csv_file import write_csv_output, get_output_file
from view.cycle_data_dialog import CycleDataDialog



class CorrectedDataWidget(QWidget):
    def __init__(self, data_processing_dialog):
        QWidget.__init__(self)

        self.data_processing_dialog = data_processing_dialog

        self.corrected_data_table = self._create_corrected_data_table()

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

        layout.addWidget(self.corrected_data_table)
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
            ratio_uncertainty_name = "uncertainty"
            if ratio.has_delta:
                column_headers.append("corrected " + ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)
                column_headers.append("uncorrected " + ratio.delta_name())
                column_headers.append(ratio_uncertainty_name)
            column_headers.append("uncorrected " + ratio.name())
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Relative distance to centre"])

        rows = []
        for sample in self.data_processing_dialog.samples:
            for spot in sample.spots:
                spot_excluded = "x" if spot.is_flagged else ""
                row = [str(sample.name + "-" + spot.id), spot_excluded]

                for ratio in method.ratios:
                    if ratio.has_delta:
                        [delta, delta_uncertainty] = spot.alpha_corrected_data[ratio]
                        [uncorrected_delta, uncorrected_delta_uncertainty] = spot.not_corrected_deltas[ratio]
                        row.append(delta)
                        row.append(delta_uncertainty)
                        row.append(uncorrected_delta)
                        row.append(uncorrected_delta_uncertainty)

                    [uncorrected_ratio, uncorrected_ratio_uncertainty] = spot.mean_two_st_error_isotope_ratios[ratio]
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

    def _create_corrected_data_table(self):

        method = self.data_processing_dialog.method

        number_of_columns = 5 + (2 * len(method.ratios))
        number_of_rows = 0

        column_headers = ["Sample name"]
        for ratio in method.ratios:
            if ratio.has_delta:
                column_headers.append("Corrected " + ratio.delta_name())
            else:
                column_headers.append("Corrected " + ratio.name())
            ratio_uncertainty_name = "uncertainty"
            column_headers.append(ratio_uncertainty_name)

        column_headers.extend(["dtfa-x", "dtfa-y", "Relative ion yield", "Distance to centre (um)"])

        for sample in self.data_processing_dialog.samples:
            number_of_rows += len(sample.spots)

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

        font_family = self.corrected_data_table.font().family()
        font = QFont(font_family, 9)

        row_number = 0
        for sample in self.data_processing_dialog.samples:
            background_colour = sample.q_colour
            for spot in sample.spots:
                row_items = []
                row_items.append(str(sample.name + " " + spot.id))

                for ratio in method.ratios:
                    if ratio.has_delta:
                        value, uncertainty = spot.alpha_corrected_data[ratio]
                        value_format = ".3f"
                        uncertainty_format = ".4f"
                    else:
                        value, uncertainty = spot.drift_corrected_ratio_values_by_ratio[ratio]
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

                    self.corrected_data_table.setItem(row_number, column_number, item)
                row_number += 1

        self.corrected_data_table.resizeColumnsToContents()

    def update_basic_table(self):
        self.corrected_data_table.clearContents()
        self._populate_basic_table()
