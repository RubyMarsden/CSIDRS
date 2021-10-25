from PyQt5.QtCore import pyqtSignal, QObject


class Signals(QObject):
    isotopesInput = pyqtSignal(list)
    materialInput = pyqtSignal(str)