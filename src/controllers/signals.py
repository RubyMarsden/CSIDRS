from PyQt5.QtCore import pyqtSignal, QObject

from src.model.elements import Element
from src.model.ratio import Ratio
from src.model.settings.material_lists import Material
from src.model.spot import Spot


class Signals(QObject):
    isotopesInput = pyqtSignal(list, Element)
    materialInput = pyqtSignal(Material)
    filenamesUpdated = pyqtSignal(list)
    sampleNamesUpdated = pyqtSignal(list)
    referenceMaterialsInput = pyqtSignal(str, str)
    cycleTreeItemChanged = pyqtSignal(int, int)
    ratioToDisplayChanged = pyqtSignal(Ratio)
    cycleFlagged = pyqtSignal(int, bool)
    spotAndCycleFlagged = pyqtSignal(Spot, int, bool, Ratio)
    recalculateNewCycleData = pyqtSignal()
    recalculateNewSpotData = pyqtSignal()
    replotAndTabulateRecalculatedData = pyqtSignal()
