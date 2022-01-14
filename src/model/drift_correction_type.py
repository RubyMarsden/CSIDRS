from enum import Enum


class DriftCorrectionType(Enum):
    LIN = "Linear"
    NONE = "None"
    QUAD = "Quadratic"