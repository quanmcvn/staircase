from src.encoding.baseline_encoding import BaselineEncoding
from src.include.common import AddClause, AuxVariable, not_, myrange_inclusive
from src.encoding.binomial_encoding import BinomialEncoding


class CommanderEncoding(BaselineEncoding):
	class GetVariableCommander:
		def __init__(self, x: list[int], k: int, num_group: int, group_size: int, aux: AuxVariable):
			self._x = x
			self._n = len(x)
			self._k = k
			self._num_group = num_group
			self._group_size = group_size
			self._c = []
			for i in myrange_inclusive(1, num_group):
				c = []
				for j in myrange_inclusive(1, k):
					c.append(aux.get_new_variable())
				self._c.append(c)

		def x(self, i: int) -> int:
			"""
			i from 1 to n
			"""
			if not (1 <= i <= self._n):
				raise RuntimeError(f"commander: i is {i} while n is {self._n}")
			return self._x[i - 1]

		def c(self, i: int, j: int) -> int:
			"""
			i from 1 to num_group \n
			j from 1 to k
			"""
			if not (1 <= i <= self._num_group):
				raise RuntimeError(f"commander: i is {i} while num_group is {self._num_group}")
			if not (1 <= j <= self._k):
				raise RuntimeError(f"commander: j is {j} while k is {self._k}")
			return self._c[i - 1][j - 1]

		def not_x(self, i: int) -> int:
			return not_(self.x(i))

		def not_c(self, i: int, j: int) -> int:
			return not_(self.c(i, j))

		def get_index_in_group(self, i: int):
			return [j for j in myrange_inclusive((i - 1) * self._group_size + 1, min(i * self._group_size, self._n))]

	def __init__(self):
		self.g = None

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		n = len(var)
		if n <= k:
			return
		group_size: int = k + 2
		num_group: int = ((n + group_size - 1) // group_size)
		self.g = CommanderEncoding.GetVariableCommander(var, k, num_group, group_size, aux)
		for i in myrange_inclusive(1, num_group):
			new_set: list[int] = []
			for x in self.g.get_index_in_group(i):
				new_set.append(self.g.x(x))
			for x in myrange_inclusive(1, k):
				new_set.append(self.g.not_c(i, x))
			BinomialEncoding().encode_at_most_k(new_set, k, aux, add_clause)
			BinomialEncoding().encode_at_least_k(new_set, k, aux, add_clause)
		# symmetry breaking
		for i in myrange_inclusive(1, num_group):
			for j in myrange_inclusive(1, k - 1):
				add_clause.add(self.g.not_c(i, j), self.g.c(i, j + 1))

		# recursively
		all_commander_variable: list[int] = []
		for i in myrange_inclusive(1, num_group):
			if i < num_group:
				for j in myrange_inclusive(1, k):
					all_commander_variable.append(self.g.c(i, j))
			else:
				size: int = n - (num_group - 1) * group_size
				size = max(size, 1)
				size = min(size, k)
				for j in myrange_inclusive(k - size + 1, k):
					all_commander_variable.append(self.g.c(i, j))

		CommanderEncoding().encode_at_most_k(all_commander_variable, k, aux, add_clause)

