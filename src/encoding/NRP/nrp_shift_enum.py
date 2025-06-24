from enum import Enum

class ShiftEnum(Enum):
    # Single shifts
	DAY_SHIFT = 0,
	EVENING_SHIFT = 1,
	NIGHT_SHIFT = 2,
	OFF_DAY = 3,
 
	# Combined shifts
	E_N_SHIFT = 4,   # EVENING_SHIFT + NIGHT_SHIFT
 
def is_valid_shift(shift: int) -> bool:
	return any(shift == e.value[0] for e in ShiftEnum)