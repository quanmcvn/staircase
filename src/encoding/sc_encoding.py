from src.encoding.baseline_encoding import BaselineEncoding
from src.include.common import AddClause, AuxVariable, not_, myrange_inclusive


class SCEncoding(BaselineEncoding):
	class GetVariableSC:
		def __init__(self, x: list[int], k: int, aux: AuxVariable):
			self._x = x
			self._n = len(x)
			self._k = k
			self._r = []
			for i in myrange_inclusive(1, self._n - 1):
				r = []
				for j in myrange_inclusive(1, k):
					r.append(aux.get_new_variable())
				self._r.append(r)

		def x(self, i: int) -> int:
			"""
			i from 1 to n
			"""
			if not (1 <= i <= self._n):
				raise RuntimeError(f"sc: i is {i} while n is {self._n}")
			return self._x[i - 1]

		def r(self, i: int, j: int) -> int:
			"""
			i from 1 to n - 1 \n
			j from 1 to k
			"""
			if not (1 <= i <= self._n - 1):
				raise RuntimeError(f"sc: i is {i} while n is {self._n}")
			if not (1 <= j <= self._k):
				raise RuntimeError(f"sc: j is {j} while k is {self._k}")
			return self._r[i - 1][j - 1]

		def not_x(self, i: int) -> int:
			return not_(self.x(i))

		def not_r(self, i: int, j: int) -> int:
			return not_(self.r(i, j))

	def __init__(self):
		self.g = None

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		n = len(var)
		self.g = SCEncoding.GetVariableSC(var, k, aux)
		if k == 0:
			for i in myrange_inclusive(1, n):
				add_clause.add(self.g.not_x(i))
			return
		else:
			for i in myrange_inclusive(1, n - 1):
				add_clause.add(self.g.not_x(i), self.g.r(i, 1))

			for j in myrange_inclusive(2, k):
				add_clause.add(self.g.not_r(1, j))

			for i in myrange_inclusive(2, n - 1):
				for j in myrange_inclusive(1, k):
					add_clause.add(self.g.not_r(i - 1, j), self.g.r(i, j))

			for i in myrange_inclusive(2, n - 1):
				for j in myrange_inclusive(2, k):
					add_clause.add(self.g.not_x(i), self.g.not_r(i - 1, j - 1), self.g.r(i, j))

			for i in myrange_inclusive(2, n):
				add_clause.add(self.g.not_x(i), self.g.not_r(i - 1, k))
