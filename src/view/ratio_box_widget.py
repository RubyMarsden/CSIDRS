from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QRadioButton


class RatioBoxWidget(QWidget):
    def __init__(self, ratios):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)

        for ratio in ratios:
            box = QRadioButton(ratio.name)
            layout.addWidget(box, alignment=Qt.AlignCenter)

        layout.addStretch()

    def emit_ratio_change_signal(self):
        return