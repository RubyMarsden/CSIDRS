from PyQt5.QtCore import pyqtSignal, QObject

from model.elements import Element
from model.ratio import Ratio
from model.settings.material_lists import Material


class Signals(QObject):
    isotopesInput = pyqtSignal(list, Element)
    materialInput = pyqtSignal(Material)
    importedFilesUpdated = pyqtSignal()
    sampleNamesUpdated = pyqtSignal()
    cycleTreeItemChanged = pyqtSignal(int, int)
    cycleFlagged = pyqtSignal(int, bool)
    recalculateNewCycleData = pyqtSignal()
    dataRecalculated = pyqtSignal()
    dataCleared = pyqtSignal()
    multipleLinearRegressionFactorsInput = pyqtSignal(list, Ratio)


signals = Signals()
