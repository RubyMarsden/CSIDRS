import matplotlib
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, QDialogButtonBox
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

from model.settings.default_filenames import cycle_data_default_filename
from utils import gui_utils
from utils.csv_utils import export_csv, request_output_csv_filename_from_user, csv_exported_successfully_popup
from view.cycle_tree_widget import CycleTreeWidget
from view.ratio_box_widget import RatioBoxWidget
from view.sample_tree import SampleTreeWidget

matplotlib.use('QT5Agg')
import matplotlib.pyplot as plt


class CycleDataDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Cycle data")
        self.setMinimumWidth(450)

        self.data_processing_dialog = data_processing_dialog
        self.model = data_processing_dialog.model

        self.sample_tree = SampleTreeWidget(self.data_processing_dialog)
        self.cycle_tree = CycleTreeWidget(self.data_processing_dialog)

        self.ratio = self.data_processing_dialog.get_current_ratio()

        self.data_processing_dialog.model.signals.cycleFlagged.connect(self.on_cycle_flagged)

        self.data_processing_dialog.model.signals.recalculateNewCycleData.connect(self.on_cycle_data_recalculated)

        layout = QHBoxLayout()
        right_layout = self._create_right_widget()
        left_layout = self._create_left_widget()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        self.sample_tree.tree.currentItemChanged.connect(self.on_sample_tree_item_selection_changed)

        self.data_processing_dialog.model.signals.cycleTreeItemChanged.connect(self.on_cycle_tree_item_changed)

        self.setLayout(layout)

        self.ratio_radiobox_widget.ratioChanged.connect(self.on_ratio_changed)
        self.ratio_radiobox_widget.set_ratio(self.ratio, block_signal=True)

    def _create_left_widget(self):
        layout = QVBoxLayout()
        self.ratio_radiobox_widget = RatioBoxWidget(self.data_processing_dialog.method.ratios)

        layout.addLayout(self._create_title_bar())
        layout.addWidget(self.ratio_radiobox_widget)
        layout.addWidget(self._create_cycle_data_graphs())

        return layout

    def _create_right_widget(self):
        layout = QVBoxLayout()
        layout.addWidget(self.sample_tree)
        self.sample_tree.set_samples(self.model.get_samples())
        self.sample_tree.select_first_spot()

        layout.addWidget(self.cycle_tree)
        self.cycle_tree.set_cycles(self.sample_tree.current_spot(), self.ratio)

        button_widget = self._create_button_widget()
        layout.addWidget(button_widget)

        return layout

    def _create_title_bar(self):
        layout = QHBoxLayout()
        title = QLabel("Ratios and cps per cycle")
        layout.addWidget(title)
        return layout

    def _create_button_widget(self):
        button_widget = QWidget()
        layout = QVBoxLayout()
        update_button = QPushButton("Recalculate data")
        update_button.clicked.connect(self.on_update_button_pushed)

        export_cycle_data_button = QPushButton("Export cycle data")
        export_cycle_data_button.clicked.connect(self.on_export_cycle_data_button_pushed)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(update_button)
        layout.addWidget(export_cycle_data_button)
        layout.addWidget(self.buttonBox)

        button_widget.setLayout(layout)

        return button_widget

    ###############
    ### Actions ###
    ###############

    def on_sample_tree_item_selection_changed(self):
        spot = self.sample_tree.current_spot()
        self.update_graphs(spot)
        self.cycle_tree.set_cycles(spot, self.ratio)

    def on_cycle_data_recalculated(self):
        self.update_graphs(self.sample_tree.current_spot())

    def on_ratio_changed(self, ratio):
        self.ratio = ratio
        self.update_graphs(self.sample_tree.current_spot())

    def on_cycle_flagged(self, cycle_number, is_flagged):
        self.data_processing_dialog.model.remove_cycle_from_spot(self.sample_tree.current_spot(),
                                                                 cycle_number, is_flagged, self.ratio)

    def on_update_button_pushed(self):
        self.data_processing_dialog.model.signals.recalculateNewCycleData.emit()

    def on_export_cycle_data_button_pushed(self):
        filename = request_output_csv_filename_from_user(cycle_data_default_filename)
        if not filename:
            return
        self.data_processing_dialog.model.export_cycle_data_csv(filename)

        csv_exported_successfully_popup(self, filename)


    ################
    ### Plotting ###
    ################

    def update_graphs(self, spot):
        self.counts_axis.clear()
        self.counts_axis2.clear()
        self.ratio_axis.clear()

        if spot:
            self.create_counts_plot(spot)
            self.create_ratio_plot(spot)

        self.canvas.draw()

    def _create_cycle_data_graphs(self):
        graph = QWidget()
        layout = QVBoxLayout()

        self.fig = plt.figure()

        self.spot_visible_grid_spec = GridSpec(2, 1)
        self.counts_axis = self.fig.add_subplot(self.spot_visible_grid_spec[0])
        self.counts_axis2 = self.counts_axis.twinx()
        self.ratio_axis = self.fig.add_subplot(self.spot_visible_grid_spec[1])

        graph_widget, self.canvas = gui_utils.create_figure_widget(self.fig, self)
        layout.addWidget(graph_widget)
        graph.setLayout(layout)

        current_spot = self.sample_tree.current_spot()
        self.create_counts_plot(current_spot)
        self.create_ratio_plot(current_spot)

        return graph

    def create_counts_plot(self, spot):
        self.counts_axis.spines['top'].set_visible(False)
        self.counts_axis.spines['right'].set_visible(False)

        y1s = spot.mass_peaks[self.ratio.numerator].detector_corrected_cps_data
        y2s = spot.mass_peaks[self.ratio.denominator].detector_corrected_cps_data

        x1s = range(1, 1 + len(y1s))
        x2s = range(1, 1 + len(y2s))

        self.counts_axis.plot(x1s, y1s, ls="", marker="x", color="red", label=self.ratio.numerator.isotope_name)
        self.counts_axis2.plot(x2s, y2s, ls="", marker="+", color="black", label=self.ratio.denominator.isotope_name)

        self.counts_axis.set_xlabel("Cycle")
        self.counts_axis.set_ylabel(str(self.ratio.numerator.isotope_name) + " (cps)")
        self.counts_axis2.set_ylabel(str(self.ratio.denominator.isotope_name) + " (cps)")
        self.counts_axis.set_xticks(x1s)
        # self.counts_axis.autoscale(enable=True, axis='y')
        axis_1_values, axis_1_labels = self.counts_axis.get_legend_handles_labels()
        axis_2_values, axis_2_labels = self.counts_axis2.get_legend_handles_labels()
        self.counts_axis2.legend(axis_1_values + axis_2_values, axis_1_labels + axis_2_labels,
                                 bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower center", borderaxespad=0, ncol=2)
        self.fig.tight_layout()

    def create_ratio_plot(self, spot):
        self.ratio_axis.spines['top'].set_visible(False)
        self.ratio_axis.spines['right'].set_visible(False)

        self.ratio_axis.set_ylabel(self.ratio.name())
        self.ratio_axis.set_xlabel("Cycle")

        ys = spot.raw_isotope_ratios[self.ratio]
        xs = list(range(1, 1 + len(ys)))

        for x, y in zip(xs, ys):
            if y in spot.outliers_removed_from_raw_data[self.ratio]:
                self.ratio_axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="navy")
            else:
                self.ratio_axis.plot(x, y, ls="", marker="o", color="navy")

        mean, two_st_error = spot.mean_two_st_error_isotope_ratios[self.ratio]
        self.ratio_axis.axhline(y=mean)

        (outlier_minimum, outlier_maximum) = spot.outlier_bounds[self.ratio]
        outlier_rectangle = Rectangle((0, outlier_minimum), len(xs) + 1, outlier_maximum - outlier_minimum)
        outlier_rectangle.set_color("lightblue")
        self.ratio_axis.add_patch(outlier_rectangle)

        st_error_rectangle = Rectangle((0, mean - two_st_error), len(xs) + 1, 2 * two_st_error)
        st_error_rectangle.set_color("cornflowerblue")
        self.ratio_axis.add_patch(st_error_rectangle)

        self.ratio_axis.set_xticks(xs)
        self.fig.tight_layout()

    def highlight_selected_ratio_data_point(self, spot, cycle_number, previous_cycle_number):
        ys = spot.raw_isotope_ratios[self.ratio]
        xs = list(range(1, 1 + len(ys)))

        for x, y in zip(xs, ys):
            if x == cycle_number:
                if y in spot.outliers_removed_from_raw_data[self.ratio]:
                    self.ratio_axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="yellow")
                else:
                    self.ratio_axis.plot(x, y, ls="", marker="o", color="yellow")

            if x == previous_cycle_number:
                if y in spot.outliers_removed_from_raw_data[self.ratio]:
                    self.ratio_axis.plot(x, y, ls="", marker="o", markerfacecolor="none", markeredgecolor="navy")
                else:
                    self.ratio_axis.plot(x, y, ls="", marker="o", color="navy")
        self.canvas.draw()

    ###############
    ### Actions ###
    ###############

    def on_cycle_tree_item_changed(self, cycle_number, previous_cycle_number):
        self.highlight_selected_ratio_data_point(self.sample_tree.current_spot(), cycle_number, previous_cycle_number)
