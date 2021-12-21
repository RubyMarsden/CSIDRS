from enum import Enum


class Element(Enum):
    def __new__(cls, *args, **kwargs):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, element_name, element_symbol):
        self.element_name = element_name
        self.element_symbol = element_symbol

    OXY = "Oxygen", "O"
    SUL = "Sulphur", "S"
    CAR = "Carbon", "C"
    CHL = "Chlorine", "Cl"
