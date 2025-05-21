from pypblib import pblib

from src.encoding.nsc_encoding import NSCEncoding
from src.encoding.pblib_encoding import PBLibEncoding
from src.include.common import AuxVariable, AddClause, myrange_inclusive, not_


class AtMostSeqCard:
	class SequentialCounter:
		class GetVariableSequentialCounter:
			def __init__(self, x: list[int], lower: int, upper: int, aux: AuxVariable, add_clause: AddClause):
				self._n = len(x)
				self._x = x
				self._lower = lower
				self._upper = upper
				# additional variable x0
				self._x0 = aux.get_new_variable()
				# set x0 <- 0
				add_clause.add(not_(self._x0))
				self._s = []
				for _ in myrange_inclusive(0, self._n):
					s = []
					for __ in myrange_inclusive(0, upper + 1):
						s.append(aux.get_new_variable())
					self._s.append(s)

			def get_x(self, i: int) -> int:
				"""
				0 <= i <= n
				"""
				if not (0 <= i <= self._n):
					raise RuntimeError(f"at_most_seq_card: get_x: i is {i} while n is {self._n}")
				if i == 0:
					return self._x0
				return self._x[i - 1]

			def get_s(self, i: int, j: int) -> int:
				"""
				0 <= i <= n
				0 <= j <= upper + 1
				"""
				if not (0 <= i <= self._n):
					raise RuntimeError(f"at_most_seq_card: get_s: i is {i} while n is {self._n}")
				if not (0 <= j <= self._upper + 1):
					raise RuntimeError(f"at_most_seq_card: get_s: j is {j} while u is {self._upper}")
				return self._s[i][j]

		def __init__(self):
			self.g = None
			pass

		def encode_range(self, var: list[int], lower: int, upper: int, aux: AuxVariable, add_clause: AddClause):
			self.g = AtMostSeqCard.SequentialCounter.GetVariableSequentialCounter(var, lower, upper, aux, add_clause)
			n = len(var)
			for i in myrange_inclusive(1, n):
				for j in myrange_inclusive(0, upper + 1):
					add_clause.add(not_(self.g.get_s(i - 1, j)), self.g.get_s(i, j))
					add_clause.add(self.g.get_x(i), not_(self.g.get_s(i, j)), self.g.get_s(i - 1, j))

			for i in myrange_inclusive(1, n):
				for j in myrange_inclusive(1, upper + 1):
					add_clause.add(not_(self.g.get_s(i, j)), self.g.get_s(i - 1, j - 1))
					add_clause.add(not_(self.g.get_x(i)), not_(self.g.get_s(i - 1, j - 1)), self.g.get_s(i, j))
			add_clause.add(self.g.get_s(0, 0))
			add_clause.add(not_(self.g.get_s(0, 1)))
			add_clause.add(self.g.get_s(n, lower))
			add_clause.add(not_(self.g.get_s(n, upper + 1)))

		def encode_c_c(self, var: list[int], d: int, aux: AuxVariable, add_clause: AddClause):
			self.encode_range(var, d, d, aux, add_clause)

		def encode_c_a(self, var: list[int], u: int, q: int, aux: AuxVariable, add_clause: AddClause):
			n = len(var)
			for i in myrange_inclusive(0, n - q):
				new_var = [var[i + j - 1] for j in myrange_inclusive(1, q)]
				self.encode_range(new_var, 0, u, aux, add_clause)

		def encode_c_s(self, var: list[int], u: int, q: int, d: int, aux: AuxVariable, add_clause: AddClause):
			self.encode_c_c(var, d, aux, add_clause)
			n = len(var)
			for i in myrange_inclusive(q, n):
				for j in myrange_inclusive(u, d + 1):
					add_clause.add(not_(self.g.get_s(i, j)), self.g.get_s(i - q, j - u))

	def __init__(self):
		pass
