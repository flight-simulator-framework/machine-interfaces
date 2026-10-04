from enum import Enum

class EnergyChangeMethod(Enum):
    DEFAULT = "default"
    QUADRUPOLE_SCALING = "quadrupole_scaling"
    BOTH = "both"