from PyQt5.QtCore import pyqtSignal, QObject

from src.model.elements import Element


class Signals(QObject):
    isotopesInput = pyqtSignal(list, Element)
    materialInput = pyqtSignal(str)
    filenamesUpdated = pyqtSignal(list)
    sampleNamesUpdated = pyqtSignal(list)
    standardsInput = pyqtSignal(str, str)
