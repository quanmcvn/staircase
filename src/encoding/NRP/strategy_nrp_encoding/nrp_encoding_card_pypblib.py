from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_strategy import NRP_Encoding_Strategy
from src.include.common import myrange_inclusive
from src.encoding.pblib_encoding import PBLibEncoding
import pypblib.pblib

# Import properties
from src.encoding.NRP.nrp_shift_enum import ShiftEnum
from src.encoding.NRP.nrp_config import NurseRosteringConfig
from src.encoding.NRP.nrp_variable import NurseRosteringVariable

class NRP_Encoding_Card_Pblib(NRP_Encoding_Strategy):
    def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, nrp_config: NurseRosteringConfig, 
                                                              nrp_variable: NurseRosteringVariable, 
                                                              upper_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            for i in myrange_inclusive(1, nrp_config.days - days + 1):
                var = [(nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
                        for j in range(days)]
                encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
                encoder.encode_at_most_k(var, upper_bound, nrp_config.aux, nrp_config.add_clause)
                del encoder
                del var
        
        
                
    def _encode_at_least_x_s_shifts_per_y_days(self, nrp_config: NurseRosteringConfig, 
                                               nrp_variable: NurseRosteringVariable, 
                                               lower_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            for i in myrange_inclusive(1, nrp_config.days - days + 1):
                var = [(nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
                        for j in range(days)]
                encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
                encoder.encode_at_least_k(var, lower_bound, nrp_config.aux, nrp_config.add_clause)
                del encoder
                del var
      
      
                
    def _encode_between_x_and_y_s_shifts_per_z_days(self, nrp_config: NurseRosteringConfig, 
                                                    nrp_variable: NurseRosteringVariable, 
                                                    lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, 
                                                    shift: ShiftEnum, days):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            for i in myrange_inclusive(1, nrp_config.days - days + 1):
                var = [(nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
                        for j in range(days)]
                encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_CARD))
                encoder.encode_range(var, lower_bound_s_shifts, upper_bound_s_shifts, nrp_config.aux,
                                        nrp_config.add_clause)
                del var
                del encoder