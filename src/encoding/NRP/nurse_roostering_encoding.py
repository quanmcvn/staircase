import pypblib.pblib

# Import environment
import sys

from src.encoding.binomial_encoding import BinomialEncoding
from src.include.common import myrange_inclusive, not_

# Import properties
from src.encoding.NRP.nrp_shift_enum import ShiftEnum
from src.encoding.NRP.nrp_config import NurseRosteringConfig
from src.encoding.NRP.nrp_variable import NurseRosteringVariable

# Import encoding strategies
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_strategy_enum import NRP_Encoding_Strategy_Enum
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_staircase import NRP_Encoding_Staircase
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_bdd_pypblib import NRP_Encoding_BDD_Pblib
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_card_pypblib import NRP_Encoding_Card_Pblib
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_card_pysat import NRP_Encoding_Card_Pysat
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_totalizer_pysat import NRP_Encoding_Totalizer_Pysat
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_kmtotalizer_pysat import NRP_Encoding_KMTotalizer_Pysat

class NurseRosteringEncoding:
	def __init__(self, nrp_config: NurseRosteringConfig):
		self.encoding_strategy = None
		self.nrp_config = nrp_config
		self.nrp_variable = NurseRosteringVariable(self.nrp_config.nurses, self.nrp_config.days, self.nrp_config.aux)
		if self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.STAIRCASE:
			self.encoding_strategy = NRP_Encoding_Staircase()
		elif self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.PBLIB_BDD:
			self.encoding_strategy = NRP_Encoding_BDD_Pblib()
		elif self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.PBLIB_CARD:
			self.encoding_strategy = NRP_Encoding_Card_Pblib()
		elif self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.PYSAT_CARD:
			self.encoding_strategy = NRP_Encoding_Card_Pysat()
		elif self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.PYSAT_TOTALIZER:
			self.encoding_strategy = NRP_Encoding_Totalizer_Pysat()
		elif self.nrp_config.encoding_type == NRP_Encoding_Strategy_Enum.PYSAT_KMTOTALIZER:
			self.encoding_strategy = NRP_Encoding_KMTotalizer_Pysat()
		else:
			print(f"Encoding strategy is not set: {self.nrp_config.encoding_type}.")
			print(f"Force stop. Return error code 1.")
			sys.exit(1)
		self._init_combined_shifts(nrp_config, self.nrp_variable)

	def _init_combined_shifts(self, nrp_config: NurseRosteringConfig, nrp_variable: NurseRosteringVariable):
		# Initialize combined shift variables
		self._init_e_n_shifts(nrp_config, nrp_variable)
		
	def _init_e_n_shifts(self, nrp_config: NurseRosteringConfig, nrp_variable: NurseRosteringVariable):
		# Initialize e_n shifts variables
		for nurse in myrange_inclusive(1, nrp_config.nurses):
			for day in myrange_inclusive(1, nrp_config.days):
				e_shift = nrp_variable.get_nurse_days_shift(nurse, day, ShiftEnum.EVENING_SHIFT.value[0])
				n_shift = nrp_variable.get_nurse_days_shift(nurse, day, ShiftEnum.NIGHT_SHIFT.value[0])
				e_n_shift = nrp_variable.get_nurse_days_shift(nurse, day, ShiftEnum.E_N_SHIFT.value[0])
    
				nrp_config.add_clause.add_list([e_shift, n_shift, not_(e_n_shift)])
				nrp_config.add_clause.add_list([not_(e_shift), e_n_shift])
				nrp_config.add_clause.add_list([not_(n_shift), e_n_shift])

	def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, upper_bound: int, shift: ShiftEnum, days: int):
		self.encoding_strategy._encode_at_most_x_s_shifts_per_y_days_using_at_least(self.nrp_config, self.nrp_variable, upper_bound, shift, days)
		
  
  

	def _encode_at_least_x_s_shifts_per_y_days(self, lower_bound: int, shift: ShiftEnum, days: int):
		self.encoding_strategy._encode_at_least_x_s_shifts_per_y_days(self.nrp_config, self.nrp_variable, lower_bound, shift, days)



	def _encode_at_most_x_workshift_per_y_days_using_at_least(self, workshifts: int, days: int):
		# at most x workshifts per y days = at least y - x offdays per y days
		self._encode_at_least_x_s_shifts_per_y_days(days - workshifts, ShiftEnum.OFF_DAY, days)



	def _encode_at_least_x_workshift_per_y_days(self, workshifts: int, days: int):
		# at least x workshifts per y days = at most y - x offdays per y days
		self._encode_at_most_x_s_shifts_per_y_days_using_at_least(days - workshifts, ShiftEnum.OFF_DAY, days)



	def _encode_between_x_and_y_s_shifts_per_z_days(self, lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, shift: ShiftEnum,
	                                                days):
		self.encoding_strategy._encode_between_x_and_y_s_shifts_per_z_days(self.nrp_config, self.nrp_variable,
                                                                     lower_bound_s_shifts, upper_bound_s_shifts,
                                                                     shift, days)



	def _encode_between_x_and_y_workshifts_per_z_days(self, lower_bound_s_shifts: int,
	                                                  upper_bound_s_shifts: int,
	                                                  days):
		self._encode_between_x_and_y_s_shifts_per_z_days(days - upper_bound_s_shifts, days - lower_bound_s_shifts,
		                                                 ShiftEnum.OFF_DAY, days)



	def _encode_at_most_x_workshifts_per_y_days_binomial(self, workshifts: int, days: int):
		# at most x workshifts per y days = at least y - x offdays per y days
		for nurse in myrange_inclusive(1, self.nrp_config.nurses):
			for i in myrange_inclusive(1, self.nrp_config.days - days + 1):
				var = [(self.nrp_variable.get_nurse_days_shift(nurse, i + j, ShiftEnum.OFF_DAY.value[0])) for j in
				       range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, days - workshifts, self.nrp_config.aux, self.nrp_config.add_clause)
				del var
				del encoder
    



	def _encode_at_least_x_s_shifts_per_y_days_binomial(self, lower_bound_shifts: int, shift: ShiftEnum, days: int):
		for nurse in myrange_inclusive(1, self.nrp_config.nurses):
			for i in myrange_inclusive(1, self.nrp_config.days - days + 1):
				var = [(self.nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0])) for j in range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, lower_bound_shifts, self.nrp_config.aux, self.nrp_config.add_clause)



	def _encode_at_most_x_s_shifts_per_y_days_binomial(self, upper_bound_shifts: int, shift: ShiftEnum, days: int):
		# at most x s shifts per 7 days = at least not y - x s shifts per y days
		for nurse in myrange_inclusive(1, self.nrp_config.nurses):
			for i in myrange_inclusive(1, self.nrp_config.days - days + 1):
				var = [not_(self.nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0])) for j in
				       range(days)]
				encoder = BinomialEncoding()
				encoder.encode_at_least_k(var, days - upper_bound_shifts, self.nrp_config.aux, self.nrp_config.add_clause)



	def _encode_ensure_nurse_1_shift_per_day(self):
		for nurse in myrange_inclusive(1, self.nrp_config.nurses):
			for day in myrange_inclusive(1, self.nrp_config.days):
				var = [self.nrp_variable.get_nurse_days_shift(nurse, day, j) for j in range(4)]
				encoder = BinomialEncoding()
				encoder.encode_exactly_k(var, 1, self.nrp_config.aux, self.nrp_config.add_clause)



	def encode(self):
		self._encode_ensure_nurse_1_shift_per_day()
		self._encode_at_most_x_workshifts_per_y_days_binomial(6, 7)
		self._encode_at_least_x_s_shifts_per_y_days(4, ShiftEnum.OFF_DAY, 14)
		self._encode_between_x_and_y_s_shifts_per_z_days(4, 8, ShiftEnum.EVENING_SHIFT, 14)
		self._encode_at_least_x_workshift_per_y_days(20, 28)
		# self._encode_at_most_x_s_shifts_per_y_days_binomial(4, ShiftEnum.NIGHT_SHIFT, 14)
		self._encode_at_most_x_s_shifts_per_y_days_using_at_least(4, ShiftEnum.NIGHT_SHIFT, 14)
		self._encode_at_least_x_s_shifts_per_y_days_binomial(1, ShiftEnum.NIGHT_SHIFT, 14)
		# self._encode_between_x_and_y_s_shifts_per_z_days(1, 4, ShiftEnum.NIGHT_SHIFT,14)
		self._encode_between_x_and_y_s_shifts_per_z_days(2, 4, ShiftEnum.E_N_SHIFT, 7)
		self._encode_at_most_x_s_shifts_per_y_days_binomial(1, ShiftEnum.NIGHT_SHIFT, 2)
