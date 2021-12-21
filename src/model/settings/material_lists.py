from enum import Enum

class Material(Enum):
    ZIR = "Zircon"
    QTZ = "Quartz"
    PYR = "Pyrite"
    PRH = "Pyrrhotite"
    CPT = "Chalcopyrite"
    PLT = "Pentlandite"
    APT = "Apatite"


oxygen_material_list = [Material.ZIR, Material.QTZ]
sulphur_material_list = [Material.PYR, Material.PRH, Material.CPT, Material.PLT, Material.APT]
chlorine_material_list = [Material.APT]