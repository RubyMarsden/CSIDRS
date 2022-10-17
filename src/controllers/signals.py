from PyQt5.QtCore import pyqtSignal, QObject

from model.drift_correction_type import DriftCorrectionType
from model.elements import Element
from model.ratio import Ratio
from model.settings.material_lists import Material
from model.spot import Spot


class Signals(QObject):
    isotopesInput = pyqtSignal(list, Element)
    materialInput = pyqtSignal(Material)
    importedFilesUpdated = pyqtSignal()
    sampleNamesUpdated = pyqtSignal()
    referenceMaterialsInput = pyqtSignal(str, str)
    cycleTreeItemChanged = pyqtSignal(int, int)
    cycleFlagged = pyqtSignal(int, bool)
    spotAndCycleFlagged = pyqtSignal(Spot, int, bool, Ratio)
    recalculateNewCycleData = pyqtSignal()
    recalculateNewSpotData = pyqtSignal()
    dataRecalculated = pyqtSignal()
    dataCleared = pyqtSignal()
    multipleLinearRegressionFactorsInput = pyqtSignal(list, Ratio)
