from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QSize


class SidrsWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
