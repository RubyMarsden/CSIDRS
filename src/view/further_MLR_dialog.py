from PyQt5.QtWidgets import QDialog, QVBoxLayout

from matplotlib import pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.dates as mdates

from utils import gui_utils
from view.ratio_box_widget import RatioBoxWidget


class FurtherMultipleLinearRegressionDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Further multiple linear regression analysis")
        self.setMinimumWidth(450)
        self.data_processing_dialog = data_processing_dialog
        self.model = data_processing_dialog.model
        self.ratio = self.data_processing_dialog.method.ratios[0]

        # Create the ratio selection button here - because the button must exist before ratio can change.
        self._create_ratio_selection_widget()

        self.data_processing_dialog.model.signals.ratioToDisplayChanged.connect(self.change_ratio)

        for sample in self.data_processing_dialog.samples:
            if sample.is_primary_reference_material:
                self.primary_reference_material_sample = sample

        layout = QVBoxLayout()
        graph_widget = self._create_graph_widget()

        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(graph_widget)

        self.setLayout(layout)

    def _create_ratio_selection_widget(self):
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios,
                                                    self.data_processing_dialog.model.signals)
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=False)

        return self.ratio_radiobox_widget

    def _create_graph_widget(self):
        self.fig = plt.figure()

        self.grid_spec = GridSpec(1, 3)
        self.time_axis = self.fig.add_subplot(self.grid_spec[0])
        self.dtfa_x_axis = self.fig.add_subplot(self.grid_spec[1], sharey=self.time_axis)
        self.dtfa_y_axis = self.fig.add_subplot(self.grid_spec[2], sharey=self.time_axis)

        self._define_ys_for_plotting()
        self._create_time_graph()
        self._create_dtfa_x_graph()
        self._create_dtfa_y_graph()

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)

        return graph_widget

    ###############
    ### Actions ###
    ###############

    def change_ratio(self, ratio):
        self.ratio = ratio
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=True)
        self.update_graphs()

    def update_graphs(self):
        self.time_axis.clear()
        self.dtfa_x_axis.clear()
        self.dtfa_y_axis.clear()

        self._define_ys_for_plotting()
        self._create_time_graph()
        self._create_dtfa_x_graph()
        self._create_dtfa_y_graph()

        self.canvas.draw()

    ################
    ### PLotting ###
    ################

    def _define_ys_for_plotting(self):
        self.ys = []
        self.yerrors = []
        for spot in self.primary_reference_material_sample.spots:
            if spot.not_corrected_deltas[self.ratio.delta_name][0]:
                if not spot.is_flagged:
                    self.ys.append(spot.not_corrected_deltas[self.ratio.delta_name][0])
                    self.yerrors.append(spot.not_corrected_deltas[self.ratio.delta_name][1])

                self.time_axis.set_ylabel(self.ratio.delta_name)
            else:
                if not spot.is_flagged:
                    self.ys.append(spot.mean_two_st_error_isotope_ratios[self.ratio][0])
                    self.yerrors.append(spot.mean_two_st_error_isotope_ratios[self.ratio][1])

                self.time_axis.set_ylabel(self.ratio.name)

    def _create_time_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            xs.append(spot.datetime)

        colour = self.primary_reference_material_sample.colour
        self.time_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)

        self.time_axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        for x_tick_label in self.time_axis.get_xticklabels():
            x_tick_label.set_rotation(30)
            x_tick_label.set_horizontalalignment('right')

        self.fig.tight_layout()

    def _create_dtfa_x_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            xs.append(spot.dtfa_x)

        colour = self.primary_reference_material_sample.colour
        self.dtfa_x_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)

    def _create_dtfa_y_graph(self):
        xs = []
        for spot in self.primary_reference_material_sample.spots:
            xs.append(spot.dtfa_y)

        colour = self.primary_reference_material_sample.colour
        self.dtfa_y_axis.errorbar(xs, self.ys, yerr=self.yerrors, marker="o", ls="", color=colour)
