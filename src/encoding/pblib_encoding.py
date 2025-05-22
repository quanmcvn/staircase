from pypblib import pblib

from src.encoding.baseline_encoding import BaselineEncoding
from src.include.common import AddClause, AuxVariable


class PBLibEncoding(BaselineEncoding):
	def __init__(self, pblib_config: pblib.PBConfig):
		self.pb2cnf = pblib.Pb2cnf(pblib_config)

	def __exit__(self):
		del self.pb2cnf

	def __del__(self):
		del self.pb2cnf

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		first_new_var = aux.get_first_new_var()
		formula = add_clause.get_clause()
		new_last_var = self.pb2cnf.encode_at_most_k(var, k, formula, first_new_var)
		aux.set_first_new_var(new_last_var + 1)

	def encode_at_least_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		first_new_var = aux.get_first_new_var()
		formula = add_clause.get_clause()
		new_last_var = self.pb2cnf.encode_at_least_k(var, k, formula, first_new_var)
		aux.set_first_new_var(new_last_var + 1)

	def encode_exactly_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		first_new_var = aux.get_first_new_var()
		formula = add_clause.get_clause()
		weights = [1 for _ in range(len(var))]
		new_last_var = self.pb2cnf.encode_both(weights, var, k, k, formula, first_new_var)
		aux.set_first_new_var(new_last_var + 1)
		del weights

	def encode_range(self, var: list[int], k: int, m: int, aux: AuxVariable, add_clause: AddClause):
		first_new_var = aux.get_first_new_var()
		formula = add_clause.get_clause()
		weights = [1 for _ in range(len(var))]
		new_last_var = self.pb2cnf.encode_both(weights, var, m, k, formula, first_new_var)
		aux.set_first_new_var(new_last_var + 1)
		del weights
