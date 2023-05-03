from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox

from view.stats_dialog import StatsWarningDialog


class CycleTreeWidget(QWidget):
    def __init__(self, data_processing_dialog):
        super().__init__()
        self.tree = QTreeWidget()
        self.data_processing_dialog = data_processing_dialog
        self.model = self.data_processing_dialog.model

        self.has_seen_stats_warning_dialog = False

        self.tree.currentItemChanged.connect(self._on_selected_cycle_change)

        self.tree.setHeaderLabel("Cycle number")
        self.buttons = self._create_next_and_back_buttons()
        self.exclude_cycle_checkbox = QCheckBox("Exclude cycle from calculations")

        self.exclude_cycle_checkbox.stateChanged.connect(self.exclude_cycle_checkbox_state_changed)

        layout = QVBoxLayout()
        layout.addWidget(self.exclude_cycle_checkbox)
        layout.addWidget(self.tree)
        layout.addWidget(self.buttons)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layout)

    def set_cycles(self, spot, ratio):
        self.tree.clear()
        if spot:
            isotope_ratios = spot.raw_isotope_ratios[ratio]
            for i, value in enumerate(isotope_ratios):
                exclude_cycle = spot.cycle_flagging_information[ratio][i]
                cycle_tree_item = QTreeWidgetItem(self.tree, [str(i+1)])
                cycle_tree_item.is_flagged = exclude_cycle

                self.highlight_cycle_tree_item(cycle_tree_item)

            any_samples = len(isotope_ratios) > 0
            self.next_item_button.setEnabled(any_samples)
            self.back_item_button.setEnabled(any_samples)
            self.select_first_cycle()

            self._on_selected_cycle_change(self.tree.currentItem(), None)

    def select_first_cycle(self):
        first_cycle = self.tree.topLevelItem(0)
        self.tree.setCurrentItem(first_cycle)

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

    ###########
    # Actions #
    ###########

    def on_next_item_clicked(self):
        self.back_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        next_item = self.tree.itemBelow(current_item)
        self.tree.setCurrentItem(next_item)

    def on_back_item_clicked(self):
        self.next_item_button.setEnabled(True)
        current_item = self.tree.currentItem()
        previous_item = self.tree.itemAbove(current_item)
        self.tree.setCurrentItem(previous_item)

    def _on_selected_cycle_change(self, current_tree_item, previous_tree_item):
        if current_tree_item:
            current_tree_item_integer = int(current_tree_item.text(0))
            if previous_tree_item is None:
                previous_tree_item_integer = 1
            else:
                previous_tree_item_integer = int(previous_tree_item.text(0))
            self.model.signals.cycleTreeItemChanged.emit(current_tree_item_integer, previous_tree_item_integer)

            next_item = self.tree.itemBelow(current_tree_item)
            self.next_item_button.setDisabled(next_item is None)

            previous_item = self.tree.itemAbove(current_tree_item)
            self.back_item_button.setDisabled(previous_item is None)

            self.exclude_cycle_checkbox.setChecked(current_tree_item.is_flagged)
        else:
            print("no current tree item")

    def highlight_cycle_tree_item(self, tree_item):
        if tree_item is None:
            tree_item = self.tree.currentItem()

        colour = QColor(255, 0, 0, 50) if tree_item.is_flagged else QColor(0, 0, 0, 0)
        tree_item.setBackground(0, colour)

    def exclude_cycle_checkbox_state_changed(self):
        if not self.has_seen_stats_warning_dialog:
            dialog = StatsWarningDialog()
            dialog.exec()
            self.has_seen_stats_warning_dialog = True
        self.tree.currentItem().is_flagged = self.exclude_cycle_checkbox.isChecked()
        self.highlight_cycle_tree_item(self.tree.currentItem())
        cycle_number = int(self.tree.currentItem().text(0)) - 1
        self.data_processing_dialog.model.signals.cycleFlagged.emit(cycle_number, self.tree.currentItem().is_flagged)

