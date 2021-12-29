from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton, QButtonGroup


class RatioBoxWidget(QWidget):
    def __init__(self, ratios, signals):
        QWidget.__init__(self)

        self.ratio_radiobuttons = []
        self.signals = signals

        self.ratio_qbutton_group = QButtonGroup()

        layout = QHBoxLayout()
        self.setLayout(layout)

        for ratio in ratios:
            button = QRadioButton(ratio.name)
            button.ratio = ratio
            layout.addWidget(button, alignment=Qt.AlignCenter)
            self.ratio_qbutton_group.addButton(button)
            button.toggled.connect(self.emit_ratio_change_signal)

            self.ratio_radiobuttons.append(button)

        layout.addStretch()

    def emit_ratio_change_signal(self):
        for button in self.ratio_radiobuttons:
            if button.isChecked():
                ratio = button.ratio

        self.signals.ratioToDisplayChanged.emit(ratio)

    def set_ratio(self, ratio):
        for button in self.ratio_radiobuttons:
            if button.ratio == ratio:
                button.setChecked(True)
            else:
                button.setChecked(False)
