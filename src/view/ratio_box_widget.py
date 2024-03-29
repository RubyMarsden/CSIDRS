from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QButtonGroup

from model.ratio import Ratio


class RatioBoxWidget(QWidget):
    ratioChanged = pyqtSignal(Ratio)

    def __init__(self, ratios):
        QWidget.__init__(self)

        self.ratio_radiobuttons = []

        self.ratio_qbutton_group = QButtonGroup()

        layout = QHBoxLayout()
        self.setLayout(layout)

        for ratio in ratios:
            button = QRadioButton(ratio.name())
            button.ratio = ratio
            layout.addWidget(button, alignment=Qt.AlignCenter)
            self.ratio_qbutton_group.addButton(button)
            # button.toggled.connect(self.emit_ratio_change_signal)

            self.ratio_radiobuttons.append(button)
        self.ratio_qbutton_group.buttonToggled.connect(self.emit_ratio_change_signal)

        layout.addStretch()

    def emit_ratio_change_signal(self, button, is_checked):
        if not is_checked:
            return

        self.ratioChanged.emit(button.ratio)

    def set_ratio(self, ratio, block_signal):
        if block_signal:
            self.ratio_qbutton_group.blockSignals(True)

        for button in self.ratio_radiobuttons:
            checked = button.ratio == ratio
            button.setChecked(checked)

        if block_signal:
            self.ratio_qbutton_group.blockSignals(False)

    def get_ratio(self):
        for button in self.ratio_radiobuttons:
            if button.isChecked():
                return button.ratio

        raise Exception("No ratio selected")
