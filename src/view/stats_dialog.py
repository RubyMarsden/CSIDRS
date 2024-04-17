from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel


class StatsWarningDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Automatic outlier removal information")
        self.setMinimumWidth(450)
        # TODO check this please
        text = "The number of outliers automatically decided by the program is calculated using the method outlined in"\
               " the paper Marsden et al. (under review). If you remove additional outliers please be sure to check if"\
               " the originally removed outliers should be incorporated into the data."
        text_widget = QLabel(text)
        text_widget.setWordWrap(True)
        layout = QHBoxLayout()
        layout.addWidget(text_widget)
        self.setLayout(layout)
