from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_strategy import NRP_Encoding_Strategy
from src.include.common import myrange_inclusive
from pysat.card import *

# Import properties
from src.encoding.NRP.nrp_shift_enum import ShiftEnum
from src.encoding.NRP.nrp_config import NurseRosteringConfig
from src.encoding.NRP.nrp_variable import NurseRosteringVariable


class NRP_Encoding_Totalizer_Pysat(NRP_Encoding_Strategy):
    def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, nrp_config: NurseRosteringConfig, 
                                                              nrp_variable: NurseRosteringVariable, 
                                                              upper_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            for i in myrange_inclusive(1, nrp_config.days - days + 1):
                var = [(nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
                        for j in range(days)]
                top_id = nrp_config.aux.get_last_used_var()
                cnf = CardEnc.atmost(lits=var, bound=upper_bound, top_id=top_id, encoding=EncType.totalizer)
                max_var = max(abs(l) for clause in cnf.clauses for l in clause)
                nrp_config.aux.set_first_new_var(max_var + 1)
                for clause in cnf.clauses:
                    nrp_config.add_clause.add_list(clause)         
                del var
            
            
                
    def _encode_at_least_x_s_shifts_per_y_days(self, nrp_config: NurseRosteringConfig, 
                                               nrp_variable: NurseRosteringVariable, 
                                               lower_bound: int, shift: ShiftEnum, days: int):
        for nurse in myrange_inclusive(1, nrp_config.nurses):
            for i in myrange_inclusive(1, nrp_config.days - days + 1):
                var = [(nrp_variable.get_nurse_days_shift(nurse, i + j, shift.value[0]))
                        for j in range(days)]
                top_id = nrp_config.aux.get_last_used_var()
                cnf = CardEnc.atleast(lits=var, bound=lower_bound, top_id=top_id, encoding=EncType.totalizer)
                max_var = max(abs(l) for clause in cnf.clauses for l in clause)
                nrp_config.aux.set_first_new_var(max_var + 1) 
                for clause in cnf.clauses:
                    nrp_config.add_clause.add_list(clause)  
                del var
        
        
                
    def _encode_between_x_and_y_s_shifts_per_z_days(self, nrp_config: NurseRosteringConfig, 
                                                    nrp_variable: NurseRosteringVariable, 
                                                    lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, 
                                                    shift: ShiftEnum, days):
        self._encode_at_most_x_s_shifts_per_y_days_using_at_least(nrp_config, nrp_variable,
                                                                 upper_bound_s_shifts, shift, days)
        self._encode_at_least_x_s_shifts_per_y_days(nrp_config, nrp_variable,
                                                    lower_bound_s_shifts, shift, days)