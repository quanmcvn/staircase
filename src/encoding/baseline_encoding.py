from abc import ABC, abstractmethod

from src.include.common import AuxVariable, AddClause


class BaselineEncoding(ABC):
	@abstractmethod
	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		pass

	def encode_at_least_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		new_var: list[int] = [-x for x in var]
		self.encode_at_most_k(new_var, len(var) - k, aux, add_clause)

	def encode_exactly_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		self.encode_at_least_k(var, k, aux, add_clause)
		self.encode_at_most_k(var, k, aux, add_clause)

	def encode_range(self, var: list[int], k: int, m: int, aux: AuxVariable, add_clause: AddClause):
		if k == m:
			return self.encode_exactly_k(var, k, aux, add_clause)
		self.encode_at_least_k(var, k, aux, add_clause)
		self.encode_at_most_k(var, m, aux, add_clause)

