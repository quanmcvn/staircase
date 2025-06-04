from pysat.card import *
from src.encoding.baseline_encoding import BaselineEncoding
from src.include.common import AddClause, AuxVariable


class PBLibCardEncodingPysat(BaselineEncoding):
	def __init__(self):
		pass

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		last_used_var = aux.get_last_used_var()
		cnf = CardEnc.atmost(lits=[var], bound=k, encoding=EncType.cardnetwrk, top_id=aux.get_last_used_var())
		for clause in cnf.clauses:
			add_clause.add(clause)
			for x in clause:
				last_used_var = max(last_used_var, x)
		aux.set_first_new_var(last_used_var + 1)

	def encode_at_least_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		last_used_var = aux.get_last_used_var()
		cnf = CardEnc.atleast(lits=[var], bound=k, encoding=EncType.cardnetwrk, top_id=aux.get_last_used_var())
		for clause in cnf.clauses:
			add_clause.add(clause)
			for x in clause:
				last_used_var = max(last_used_var, x)
		aux.set_first_new_var(last_used_var + 1)

	def encode_exactly_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		last_used_var = aux.get_last_used_var()
		cnf = CardEnc.equals(lits=[var], bound=k, encoding=EncType.cardnetwrk, top_id=aux.get_last_used_var())
		for clause in cnf.clauses:
			add_clause.add(clause)
			for x in clause:
				last_used_var = max(last_used_var, x)
		aux.set_first_new_var(last_used_var + 1)
