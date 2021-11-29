from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton


class RatioBoxWidget(QWidget):
    def __init__(self, ratios, signals):
        QWidget.__init__(self)

        self.ratio_radiobuttons = []
        self.signals = signals

        layout = QHBoxLayout()
        self.setLayout(layout)

        for ratio in ratios:
            button = QRadioButton(ratio.name)
            button.ratio = ratio
            layout.addWidget(button, alignment=Qt.AlignCenter)
            button.toggled.connect(self.emit_ratio_change_signal)

            self.ratio_radiobuttons.append(button)

        layout.addStretch()

    def emit_ratio_change_signal(self):
        for button in self.ratio_radiobuttons:
            if button.isChecked():
                ratio = button.ratio

        self.signals.ratioToDisplayChanged.emit(ratio)

        print(ratio.name)
