from abc import ABC, abstractmethod

from enum import Enum

# Import properties
from src.encoding.NRP.nrp_shift_enum import ShiftEnum
from src.encoding.NRP.nrp_config import NurseRosteringConfig
from src.encoding.NRP.nrp_variable import NurseRosteringVariable

class NRP_Encoding_Strategy(ABC):
    @abstractmethod
    def _encode_at_most_x_s_shifts_per_y_days_using_at_least(self, nrp_config: NurseRosteringConfig, 
                                                              nrp_variable: NurseRosteringVariable, 
                                                              upper_bound: int, shift: ShiftEnum, days: int):
        pass
    
    
    
    @abstractmethod
    def _encode_at_least_x_s_shifts_per_y_days(self, nrp_config: NurseRosteringConfig, 
                                               nrp_variable: NurseRosteringVariable, 
                                               lower_bound: int, shift: ShiftEnum, days: int):
        pass
    
    
    
    @abstractmethod
    def _encode_between_x_and_y_s_shifts_per_z_days(self, nrp_config: NurseRosteringConfig, 
                                                    nrp_variable: NurseRosteringVariable, 
                                                    lower_bound_s_shifts: int,
	                                                upper_bound_s_shifts: int, 
                                                    shift: ShiftEnum, days):
        pass