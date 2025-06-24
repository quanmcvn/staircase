from enum import Enum

class NRP_Encoding_Strategy_Enum(Enum):
    STAIRCASE = 0,
    PBLIB_BDD = 1,
    PBLIB_CARD = 2,         # Use PYSAT_CARD instead
    PYSAT_CARD = 3,
    PYSAT_TOTALIZER = 4,    # Use PYSAT_KMTOTALIZER instead
    PYSAT_KMTOTALIZER = 5,
