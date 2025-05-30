from enum import Enum

class NRP_Encoding_Strategy_Enum(Enum):
    STAIRCASE = 0,
    PBLIB_BDD = 1,
    PBLIB_CARD = 2,
    PYSAT_CARD = 3,
    PYSAT_TOTALIZER = 4,
