from enum import Enum

class ShiftEnum(Enum):
	DAY_SHIFT = 0,
	EVENING_SHIFT = 1,
	NIGHT_SHIFT = 2,
	OFF_DAY = 3,
 
def is_valid_shift(shift: int) -> bool:
	return any(shift == e.value[0] for e in ShiftEnum)