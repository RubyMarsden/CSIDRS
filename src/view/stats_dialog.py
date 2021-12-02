from PyQt5.QtWidgets import QDialog


class StatsWarningDialog(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.setWindowTitle("Outlier removal discussion")
        self.setMinimumWidth(450)