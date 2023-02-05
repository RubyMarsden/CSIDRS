from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QWidget, QDialogButtonBox, QHBoxLayout, QPushButton

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from utils import gui_utils
from view.ratio_box_widget import RatioBoxWidget

from model.spot import SpotAttribute


class FurtherMultipleLinearRegressionDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Further multiple linear regression analysis")
        self.setMinimumWidth(450)
        self.data_processing_dialog = data_processing_dialog
        self.model = data_processing_dialog.model
        self.signals = data_processing_dialog.model.signals
        self.ratio = self.data_processing_dialog.get_current_ratio()
        self.spot_attribute_box_list = []
        self.spot_attributes = []

        # Create the ratio selection button here - because the button must exist before ratio can change.
        self._create_ratio_selection_widget()

        self.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)

        for sample in self.data_processing_dialog.model.get_samples():
            if sample.is_primary_reference_material:
                self.primary_reference_material_sample = sample

        self.calculate_mlr_using_selected_factors_button = QPushButton("Calculate MLR")
        self.calculate_mlr_using_selected_factors_button.clicked.connect(self.on_calculate_mlr_button_clicked)

        layout = QVBoxLayout()
        layout_horizontal = QHBoxLayout()
        graph_widget = self._create_graph_widget()

        options_for_mlr_widget = self._create_options_for_mlr_widget()

        layout.addWidget(self.ratio_radiobox_widget)
        layout_horizontal.addWidget(graph_widget)
        layout_horizontal.addWidget(options_for_mlr_widget)
        layout.addLayout(layout_horizontal)
        layout.addWidget(self.calculate_mlr_using_selected_factors_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios)
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=False)

        return self.ratio_radiobox_widget

    def _create_graph_widget(self):
        self.fig = plt.figure()

        self.grid_spec = GridSpec(2, 2)
        self.time_axis = self.fig.add_subplot(self.grid_spec[0, 0])
        self.dtfa_x_axis = self.fig.add_subplot(self.grid_spec[1, 0], sharey=self.time_axis)
        self.dtfa_y_axis = self.fig.add_subplot(self.grid_spec[0, 1], sharey=self.time_axis)
        self.distance_to_mount_centre_axis = self.fig.add_subplot(self.grid_spec[1, 1], sharey=self.time_axis)

        self._define_ys_for_plotting()
        self._create_time_graph()
        self._create_dtfa_x_graph()
        self._create_dtfa_y_graph()
        self._create_distance_to_mount_centre_graph()

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

    def _create_options_for_mlr_widget(self):
        mlr_widget = QWidget()
        layout = QVBoxLayout()
        for spot_attribute in SpotAttribute:
            box = QCheckBox(spot_attribute.value)
            box.attribute = spot_attribute
            box.stateChanged.connect(self.on_spot_attributes_changed)
            layout.addWidget(box)
            self.spot_attribute_box_list.append(box)

        mlr_widget.setLayout(layout)
        return mlr_widget

    ###############
    ### Actions ###
    ###############

    def on_ratio_changed(self, ratio):
        self.ratio = ratio
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=True)
        self.update_graphs()

    def update_graphs(self):
        self.time_axis.clear()
        self.dtfa_x_axis.clear()
        self.dtfa_y_axis.clear()
        self.distance_to_mount_centre_axis.clear()

        self._define_ys_for_plotting()
        self._create_time_graph()
        self._create_dtfa_x_graph()
        self._create_dtfa_y_graph()
        self._create_distance_to_mount_centre_graph()

        self.canvas.draw()

    def on_spot_attributes_changed(self):
        self.spot_attributes.clear()
        for box in self.spot_attribute_box_list:
            if box.isChecked():
                self.spot_attributes.append(box.attribute)

        #TODO this please
        #if self.spot_attributes:
         #   self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

    def on_calculate_mlr_button_clicked(self):
        for spot_attribute in self.spot_attributes:
            print(spot_attribute == SpotAttribute.TIME)

        self.signals.multipleLinearRegressionFactorsInput.emit(self.spot_attributes, self.ratio)


    ################
    ### PLotting ###
    ################

    def _define_ys_for_plotting(self):
        self.ys = []
        self.yerrors = []
        for spot in self.primary_reference_material_sample.spots:
            if self.ratio.has_delta:
                if not spot.is_flagged:
                    self.ys.append(spot.not_corrected_deltas[self.ratio][0])
                    self.yerrors.append(spot.not_corrected_deltas[self.ratio][1])

                self.time_axis.set_ylabel(self.ratio.delta_name())
            else:
                if not spot.is_flagged:
                    self.ys.append(spot.mean_two_st_error_isotope_ratios[self.ratio][0])
                    self.yerrors.append(spot.mean_two_st_error_isotope_ratios[self.ratio][1])

                self.time_axis.set_ylabel(self.ratio.name())

    def _create_time_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            if not spot.is_flagged:
                xs.append(spot.datetime)

        colour = self.primary_reference_material_sample.colour
        self.time_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)

        self.time_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        for x_tick_label in self.time_axis.get_xticklabels():
            x_tick_label.set_rotation(30)
            x_tick_label.set_horizontalalignment('right')

        self.time_axis.set_xlabel("Time")

        self.fig.tight_layout()

    def _create_dtfa_x_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            if not spot.is_flagged:
                xs.append(spot.dtfa_x)

        colour = self.primary_reference_material_sample.colour
        self.dtfa_x_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)
        self.dtfa_x_axis.set_xlabel("dtfa-x")

    def _create_dtfa_y_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            if not spot.is_flagged:
                xs.append(spot.dtfa_y)

        colour = self.primary_reference_material_sample.colour
        self.dtfa_y_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)

        self.dtfa_y_axis.set_xlabel("dtfa-y")

    def _create_distance_to_mount_centre_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            if not spot.is_flagged:
                xs.append(spot.distance_from_mount_centre)

        colour = self.primary_reference_material_sample.colour
        self.distance_to_mount_centre_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)

        self.distance_to_mount_centre_axis.set_xlabel("Relative distance to mount centre")