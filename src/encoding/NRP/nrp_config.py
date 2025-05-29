from src.include.common import AuxVariable, AddClause
from src.encoding.NRP.strategy_nrp_encoding.nrp_encoding_strategy_enum import NRP_Encoding_Strategy_Enum

class NurseRosteringConfig:
	def __init__(self, nurses: int, days: int, aux: AuxVariable, add_clause: AddClause, encoding_type: NRP_Encoding_Strategy_Enum):
		self.nurses = nurses
		self.days = days
		self.aux = aux
		self.add_clause = add_clause
		self.encoding_type = encoding_type