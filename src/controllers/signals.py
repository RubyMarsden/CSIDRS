from PyQt5.QtCore import pyqtSignal, QObject

from src.model.elements import Element
from src.model.ratio import Ratio


class Signals(QObject):
    isotopesInput = pyqtSignal(list, Element)
    materialInput = pyqtSignal(str)
    filenamesUpdated = pyqtSignal(list)
    sampleNamesUpdated = pyqtSignal(list)
    referenceMaterialsInput = pyqtSignal(str, str)
    cycleTreeItemChanged = pyqtSignal(int, int)
    ratioToDisplayChanged = pyqtSignal(Ratio)
