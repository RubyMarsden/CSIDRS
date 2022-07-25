from enum import Enum

from model.elements import Element


class Material(Enum):
    ZIR = "Zircon"
    QTZ = "Quartz"
    PYR = "Pyrite"
    PRH = "Pyrrhotite"
    CPT = "Chalcopyrite"
    PLT = "Pentlandite"
    APT = "Apatite"


materials_by_element = {
    Element.OXY: [Material.ZIR, Material.QTZ],
    Element.SUL: [Material.PYR, Material.PRH, Material.CPT, Material.PLT, Material.APT],
    Element.CHL: [Material.APT]
}
