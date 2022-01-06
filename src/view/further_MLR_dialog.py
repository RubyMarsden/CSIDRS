from PyQt5.QtWidgets import QDialog


class FurtherMultipleLinearRegressionDialog(QDialog):
    def __init__(self, data_processing_dialog):
        QDialog.__init__(self)
        self.setWindowTitle("Further multiple linear regression analysis")
        self.setMinimumWidth(450)
