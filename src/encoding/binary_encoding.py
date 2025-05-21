from src.encoding.baseline_encoding import BaselineEncoding
from src.include.common import AddClause, AuxVariable, not_, myrange_inclusive


class BinaryEncoding(BaselineEncoding):
	class GetVariableBinary:
		def __init__(self, x: list[int], k: int, aux: AuxVariable):
			self._x = x
			self._n = len(x)
			self._k = k
			self._log2 = 0
			for log2 in myrange_inclusive(0, 32):
				if 2 ** log2 >= self._n:
					self._log2 = log2
					break
			self._b = []
			for i in myrange_inclusive(1, k):
				b = []
				for j in myrange_inclusive(1, self._log2):
					b.append(aux.get_new_variable())
				self._b.append(b)
			self._t = []
			for i in myrange_inclusive(1, k):
				t = []
				for j in myrange_inclusive(1, self._n):
					t.append(aux.get_new_variable())
				self._t.append(t)

		def x(self, i: int) -> int:
			"""
			i from 1 to n
			"""
			if not (1 <= i <= self._n):
				raise RuntimeError(f"binary: i is {i} while n is {self._n}")
			return self._x[i - 1]

		def b(self, i: int, j: int) -> int:
			"""
			i from 1 to k \n
			j from 1 to log2(n)
			"""
			if not (1 <= i <= self._k):
				raise RuntimeError(f"binary: i is {i} while k is {self._k}")
			if not (1 <= j <= self._log2):
				raise RuntimeError(f"binary: j is {j} while log2 is {self._log2}")
			return self._b[i - 1][j - 1]

		def t(self, i: int, j: int) -> int:
			"""
			i from 1 to k \n
			j from 1 to n
			"""
			if not (1 <= i <= self._k):
				raise RuntimeError(f"binary: i is {i} while k is {self._k}")
			if not (1 <= j <= self._n):
				raise RuntimeError(f"binary: j is {j} while n is {self._n}")
			return self._t[i - 1][j - 1]

		def not_x(self, i: int) -> int:
			return not_(self.x(i))

		def not_b(self, i: int, j: int) -> int:
			return not_(self.b(i, j))

		def not_t(self, i: int, j: int) -> int:
			return not_(self.t(i, j))

		def get_log2(self) -> int:
			return self._log2

	def __init__(self):
		self.g = None

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		n = len(var)
		self.g = BinaryEncoding.GetVariableBinary(var, k, aux)
		for i in myrange_inclusive(1, n):
			ts = [self.g.not_x(i)]
			for j in myrange_inclusive(1, k):
				ts.append(self.g.t(j, i))
			add_clause.add_list(ts)
			for j in myrange_inclusive(1, self.g.get_log2()):
				for gr in myrange_inclusive(1, k):
					if i >> (j - 1) & 1:
						b = self.g.b(gr, j)
					else:
						b = self.g.not_b(gr, j)
					add_clause.add(self.g.not_t(gr, i), b)
