from PyQt5.QtWidgets import QDialog, QLayout


class DataProcessingDialog(QDialog):
    def __init__(self):

        right_layout = self._create_right_layout()
        left_layout = self._create_left_layout()

    def _create_right_layout(self):
        layout = QLayout()
        return layout

    def _create_left_layout(self):
        layout = QLayout()
        return layout
