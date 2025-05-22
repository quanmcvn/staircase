import pypblib.pblib

from src.encoding.binomial_encoding import BinomialEncoding
from src.encoding.pblib_encoding import PBLibEncoding
from src.encoding.staircase_encoding import StaircaseEncoding
from src.include.common import AuxVariable, AddClause, myrange_inclusive, not_
from enum import Enum


class ShiftEnum(Enum):
	DAY_SHIFT = 0,
	EVENING_SHIFT = 1,
	NIGHT_SHIFT = 2,
	OFF_DAY = 3,


class NurseRosteringConfig:
	def __init__(self, nurses: int, days: int, aux: AuxVariable, add_clause: AddClause, encoding_type: str):
		self.nurses = nurses
		self.days = days
		self.aux = aux
		self.add_clause = add_clause
		self.encoding_type = encoding_type
		if encoding_type not in ['staircase', 'pblib_bdd', 'pblib_card']:
			raise RuntimeError(f"NurseRosteringConfig: unrecognized encoding type {encoding_type}")


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


class NurseRosteringEncoding:
	def __init__(self, config: NurseRosteringConfig):
		self.config = config
		self.nurse_variable = NurseRosteringVariable(self.config.nurses, self.config.days, self.config.aux)

	def __del(self):
		del self.nurse_variable

	def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, upper_bound: int, shift: ShiftEnum, days: int):
		if self.config.encoding_type == 'staircase':
			for nurse in myrange_inclusive(1, self.config.nurses):
				var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
				       myrange_inclusive(1, self.config.days)]
				encoder = StaircaseEncoding()
				encoder.encode_staircase_at_least(var, days, days - upper_bound, self.config.aux,
				                                  self.config.add_clause)
				del var
		elif self.config.encoding_type == 'pblib_bdd':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BDD))
					encoder.encode_at_most_k(var, upper_bound, self.config.aux, self.config.add_clause)
					del encoder
					del var
		elif self.config.encoding_type == 'pblib_card':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
					encoder.encode_at_most_k(var, upper_bound, self.config.aux, self.config.add_clause)
					del encoder
					del var
		else:
			raise RuntimeError(
				f"_encode_at_most_x_s_shifts_per_y_days_using_at_least: unregconized type {self.config.encoding_type}")

	def _encode_at_least_x_s_shifts_per_y_days(self, lower_bound: int, shift: ShiftEnum, days: int):
		if self.config.encoding_type == 'staircase':
			for nurse in myrange_inclusive(1, self.config.nurses):
				var = [(self.nurse_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
				       myrange_inclusive(1, self.config.days)]
				encoder = StaircaseEncoding()
				encoder.encode_staircase_at_least(var, days, lower_bound, self.config.aux, self.config.add_clause)
				del var
		elif self.config.encoding_type == 'pblib_bdd':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BDD))
					encoder.encode_at_least_k(var, lower_bound, self.config.aux, self.config.add_clause)
					del encoder
					del var
		elif self.config.encoding_type == 'pblib_card':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
					encoder.encode_at_least_k(var, lower_bound, self.config.aux, self.config.add_clause)
					del encoder
					del var
		else:
			raise RuntimeError(f"_encode_at_least_x_s_shifts_per_y_days: unregconized type {self.config.encoding_type}")

	def _encode_at_most_x_workshift_per_y_days_using_at_least(self, workshifts: int, days: int):
		# at most x workshifts per y days = at least y - x offdays per y days
		self._encode_at_least_x_s_shifts_per_y_days(days - workshifts, ShiftEnum.OFF_DAY, days)

	def _encode_at_least_x_workshift_per_y_days(self, workshifts: int, days: int):
		if self.config.encoding_type == 'staircase':
			for nurse in myrange_inclusive(1, self.config.nurses):
				var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, j, ShiftEnum.OFF_DAY.value[0])) 
           				for j in myrange_inclusive(1, self.config.days)]
				encoder = StaircaseEncoding()
				encoder.encode_staircase_at_least(var, days, workshifts, self.config.aux, self.config.add_clause)
		elif self.config.encoding_type == 'pblib_bdd':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, i + j, ShiftEnum.OFF_DAY.value[0]))
					        for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BDD))
					encoder.encode_at_least_k(var, workshifts, self.config.aux, self.config.add_clause)
		elif self.config.encoding_type == 'pblib_card':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, i + j, ShiftEnum.OFF_DAY.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
					encoder.encode_at_least_k(var, workshifts, self.config.aux, self.config.add_clause)
		else:
			raise RuntimeError(f"_encode_at_least_x_s_shifts_per_y_days: unregconized type {self.config.encoding_type}")


	def _encode_between_x_and_y_s_shifts_per_z_days(self, lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, shift: ShiftEnum,
	                                                days):
		if self.config.encoding_type == 'staircase':
			# at least x s shift per z days
			# at most y s shift per z days = at least not z - y s shift per z days
			for nurse in myrange_inclusive(1, self.config.nurses):
				var = [(self.nurse_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
				       myrange_inclusive(1, self.config.days)]
				encoder = StaircaseEncoding()
				encoder.encode_staircase_at_least(var, days, lower_bound_s_shifts, self.config.aux,
				                                  self.config.add_clause)
				del var
			for nurse in myrange_inclusive(1, self.config.nurses):
				var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
				       myrange_inclusive(1, self.config.days)]
				encoder = StaircaseEncoding()
				encoder.encode_staircase_at_least(var, days, days - upper_bound_s_shifts, self.config.aux,
				                                  self.config.add_clause)
				del var
		elif self.config.encoding_type == 'pblib_bdd':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BDD))
					encoder.encode_range(var, lower_bound_s_shifts, upper_bound_s_shifts, self.config.aux,
					                     self.config.add_clause)
					del var
					del encoder
		elif self.config.encoding_type == 'pblib_card':
			for nurse in myrange_inclusive(1, self.config.nurses):
				for i in myrange_inclusive(1, self.config.days - days + 1):
					var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
					       for j in range(days)]
					encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
					encoder.encode_range(var, lower_bound_s_shifts, upper_bound_s_shifts, self.config.aux,
					                     self.config.add_clause)
					del var
					del encoder
		else:
			raise RuntimeError(
				f"_encode_between_x_and_y_s_shifts_per_z_days: unregconized type {self.config.encoding_type}")

	def _encode_between_x_and_y_workshifts_per_z_days(self, lower_bound_s_shifts: int,
	                                                  upper_bound_s_shifts: int,
	                                                  days):
		self._encode_between_x_and_y_s_shifts_per_z_days(days - upper_bound_s_shifts, days - lower_bound_s_shifts,
		                                                 ShiftEnum.OFF_DAY, days)

	def _encode_at_most_x_workshifts_per_y_days_binomial(self, workshifts: int, days: int):
		# at most x workshifts per y days = at least y - x offdays per y days
		for nurse in myrange_inclusive(1, self.config.nurses):
			for i in myrange_inclusive(1, self.config.days - days + 1):
				var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, ShiftEnum.OFF_DAY.value[0])) for j in
				       range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, days - workshifts, self.config.aux, self.config.add_clause)
				del var

	def _encode_at_least_x_s_shifts_per_y_days_binomial(self, lower_bound_shifts: int, shift: ShiftEnum, days: int):
		for nurse in myrange_inclusive(1, self.config.nurses):
			for i in myrange_inclusive(1, self.config.days - days + 1):
				var = [(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0])) for j in range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, lower_bound_shifts, self.config.aux, self.config.add_clause)

	def _encode_at_most_x_s_shifts_per_y_days_binomial(self, upper_bound_shifts: int, shift: ShiftEnum, days: int):
		# at most x s shifts per 7 days = at least not y - x s shifts per y days
		for nurse in myrange_inclusive(1, self.config.nurses):
			for i in myrange_inclusive(1, self.config.days - days + 1):
				var = [not_(self.nurse_variable.get_nurse_days_shift(nurse, i + j, shift.value[0])) for j in
				       range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, days - upper_bound_shifts, self.config.aux, self.config.add_clause)

	def _encode_ensure_nurse_1_shift_per_day(self):
		for nurse in myrange_inclusive(1, self.config.nurses):
			for day in myrange_inclusive(1, self.config.days):
				var = [self.nurse_variable.get_nurse_days_shift(nurse, day, j) for j in range(4)]
				encoder = BinomialEncoding()
				encoder.encode_exactly_k(var, 1, self.config.aux, self.config.add_clause)

	def encode(self):
		self._encode_ensure_nurse_1_shift_per_day()
		self._encode_at_most_x_workshifts_per_y_days_binomial(6, 7)
		self._encode_at_least_x_s_shifts_per_y_days(4, ShiftEnum.OFF_DAY, 14)
		self._encode_between_x_and_y_s_shifts_per_z_days(4, 8, ShiftEnum.EVENING_SHIFT, 14)
		self._encode_at_least_x_workshift_per_y_days(19, 28)
		self._encode_at_most_x_s_shifts_per_y_days_binomial(2, ShiftEnum.NIGHT_SHIFT, 7)
		self._encode_at_least_x_s_shifts_per_y_days_binomial(1, ShiftEnum.NIGHT_SHIFT, 14)
		self._encode_between_x_and_y_s_shifts_per_z_days(2, 4, ShiftEnum.EVENING_SHIFT, 7)
		self._encode_at_most_x_s_shifts_per_y_days_binomial(1, ShiftEnum.NIGHT_SHIFT, 2)
