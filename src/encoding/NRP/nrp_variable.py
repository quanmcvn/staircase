from src.include.common import AuxVariable

class NurseRosteringVariable:
	def __init__(self, nurses: int, days: int, aux: AuxVariable):
		# nurse[i][d][s] = nurse with id i on day d chooses shift s
		self.nurse = []
		for _i in range(nurses):
			nurse_i = []
			for _j in range(days):
				# 4 shifts are D (day), E (evening), N (night), O (offday)
				shifts = [aux.get_new_variable() for _ in range(4)]
				nurse_i.append(shifts)
			self.nurse.append(nurse_i)



	def __del__(self):
		del self.nurse



	def get_nurse_days_shift(self, nurse: int, day: int, shift: int) -> int:
		if not (1 <= nurse <= len(self.nurse)):
			raise RuntimeError(f"NurseRosteringVariable: nurse is {nurse} but max nurse {len(self.nurse)}")
		if not (1 <= day <= len(self.nurse[0])):
			raise RuntimeError(f"NurseRosteringVariable: day is {day} but max day {len(self.nurse[0])}")
		if not (0 <= shift < 4):
			raise RuntimeError(f"NurseRosteringVariable: shift is {shift} (min 0 max 3)")
		return self.nurse[nurse - 1][day - 1][shift]
