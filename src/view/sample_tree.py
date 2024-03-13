from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox

from controllers.signals import signals


class SampleTreeWidget(QWidget):
    def __init__(self, data_processing_dialog):
        super().__init__()
        self.data_processing_dialog = data_processing_dialog
        self.tree = QTreeWidget()
        self.exclude_spot_checkbox = QCheckBox("Exclude spot from calculations")

        self.exclude_spot_checkbox.stateChanged.connect(self.on_exclude_spot_checkbox_state_changed)

        self.tree.currentItemChanged.connect(self._on_selected_sample_change)
        self.tree.setHeaderLabel("Samples")

        self.buttons = self._create_next_and_back_buttons()

        layout = QVBoxLayout()
        layout.addWidget(self.exclude_spot_checkbox)
        layout.addWidget(self.tree)
        layout.addWidget(self.buttons)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def set_samples(self, samples):
        self.tree.clear()
        for sample in samples:
            sample_tree_item = QTreeWidgetItem(self.tree, [sample.name])
            sample_tree_item.sample = sample
            sample_tree_item.is_sample = True
            colour = sample_tree_item.sample.q_colour
            sample_tree_item.setBackground(0, colour)
            for spot in sample.spots:
                spot_tree_item = QTreeWidgetItem(sample_tree_item, [spot.id])
                spot_tree_item.spot = spot
                spot_tree_item.is_sample = False
                spot_tree_item.cycles = []
        any_samples = len(samples) > 0
        self.next_item_button.setEnabled(any_samples)
        self.back_item_button.setEnabled(any_samples)
        self.select_first_spot()

    def select_first_spot(self):
        first_sample = self.tree.topLevelItem(0)
        if not first_sample:
            return
        first_spot = first_sample.child(0)
        self.tree.setCurrentItem(first_spot)

    def _create_next_and_back_buttons(self):

        self.next_item_button = QPushButton("Next")
        self.next_item_button.clicked.connect(self.on_next_item_clicked)
        self.back_item_button = QPushButton("Back")
        self.back_item_button.clicked.connect(self.on_back_item_clicked)

        self.next_item_button.setDisabled(True)
        self.back_item_button.setDisabled(True)

        layout = QHBoxLayout()
        layout.addWidget(self.back_item_button)
        layout.addWidget(self.next_item_button)

        widget = QWidget()
        widget.setLayout(layout)

        return widget

    def current_spot(self):
        current_item = self.tree.currentItem()
        if current_item is None or current_item.is_sample:
            return None
        return current_item.spot

    #######
    # Actions
    #######

    def on_next_item_clicked(self):
        self.back_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        next_item = self.tree.itemBelow(current_item)
        if current_item.is_sample and current_item.childCount() > 0:
            next_item = current_item.child(0)

        self.tree.setCurrentItem(next_item)

    def on_back_item_clicked(self):
        self.next_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        previous_item = self.tree.itemAbove(current_item)
        self.tree.setCurrentItem(previous_item)

    def _on_selected_sample_change(self, current_tree_item, previous_tree_item):
        if current_tree_item is None:
            return

        next_item = self.tree.itemBelow(current_tree_item)
        self.next_item_button.setDisabled(next_item is None)

        previous_item = self.tree.itemAbove(current_tree_item)
        self.back_item_button.setDisabled(previous_item is None)

        if current_tree_item.is_sample:
            self.exclude_spot_checkbox.setChecked(False)
            self.exclude_spot_checkbox.setEnabled(False)
        else:
            self.exclude_spot_checkbox.setEnabled(True)
            self.exclude_spot_checkbox.setChecked(current_tree_item.spot.is_flagged)

    def highlight_spot(self, is_flagged):
        current_tree_item = self.tree.currentItem()
        if current_tree_item.is_sample:
            return

        colour = QColor(255, 0, 0, 50) if is_flagged else QColor(0, 0, 0, 0)
        current_tree_item.setBackground(0, colour)

    def on_exclude_spot_checkbox_state_changed(self):
        # TODO if this is a sample what happens? causes attribute error if you go from a flagged spot to a sample
        #  name in the tree.
        self.current_spot().is_flagged = self.exclude_spot_checkbox.isChecked()
        self.highlight_spot(self.current_spot().is_flagged)
        primary_rm = self.data_processing_dialog.model.get_primary_reference_material()
        method = self.data_processing_dialog.model.method
        samples = self.data_processing_dialog.model.get_samples()
        drift_correction_type_by_ratio = self.data_processing_dialog.model.drift_correction_type_by_ratio
        element = self.data_processing_dialog.model.element
        material = self.data_processing_dialog.model.material
        self.data_processing_dialog.model.calculation_results.calculate_data_from_drift_correction_onwards(primary_rm,
                                                                                                           method,
                                                                                                           samples,
                                                                                                           drift_correction_type_by_ratio,
                                                                                                           element,
                                                                                                           material)
        signals.dataRecalculated.emit()


