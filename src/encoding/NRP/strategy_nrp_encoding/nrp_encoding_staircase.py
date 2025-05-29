from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_strategy import NRP_Encoding_Strategy
from src.include.common import myrange_inclusive, not_
from src.encoding.staircase_encoding import StaircaseEncoding

# Import properties
from src.encoding.NRP.nrp_shift_enum import ShiftEnum
from src.encoding.NRP.nrp_config import NurseRosteringConfig
from src.encoding.NRP.nrp_variable import NurseRosteringVariable

class NRP_Encoding_Staircase(NRP_Encoding_Strategy):
    def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, nrp_config: NurseRosteringConfig, 
                                                              nrp_variable: NurseRosteringVariable, 
                                                              upper_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            var = [not_(nrp_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
                    myrange_inclusive(1, nrp_config.days)]
            encoder = StaircaseEncoding()
            encoder.encode_staircase_at_least(var, days, days - upper_bound, nrp_config.aux,
                                                nrp_config.add_clause)
            del var
            del encoder
      
      
            
    def _encode_at_least_x_s_shifts_per_y_days(self, nrp_config: NurseRosteringConfig, 
                                               nrp_variable: NurseRosteringVariable, 
                                               lower_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            var = [(nrp_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
                    myrange_inclusive(1, nrp_config.days)]
            encoder = StaircaseEncoding()
            encoder.encode_staircase_at_least(var, days, lower_bound, nrp_config.aux, nrp_config.add_clause)
            del var
         
         
            
    def _encode_between_x_and_y_s_shifts_per_z_days(self, nrp_config: NurseRosteringConfig, 
                                                    nrp_variable: NurseRosteringVariable, 
                                                    lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, 
                                                    shift: ShiftEnum, days):
        # at least x s shift per z days
        # at most y s shift per z days = at least not z - y s shift per z days
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            var = [(nrp_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
                    myrange_inclusive(1, nrp_config.days)]
            encoder = StaircaseEncoding()
            encoder.encode_staircase_at_least(var, days, lower_bound_s_shifts, nrp_config.aux,
                                                nrp_config.add_clause)
            del var
            del encoder
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            var = [not_(nrp_variable.get_nurse_days_shift(nurse, j, shift.value[0])) for j in
                    myrange_inclusive(1, nrp_config.days)]
            encoder = StaircaseEncoding()
            encoder.encode_staircase_at_least(var, days, days - upper_bound_s_shifts, nrp_config.aux,
                                                nrp_config.add_clause)
            del var
            del encoder