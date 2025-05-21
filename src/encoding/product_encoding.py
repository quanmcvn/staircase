from src.encoding.baseline_encoding import BaselineEncoding
from src.encoding.binomial_encoding import BinomialEncoding
from src.include.common import AddClause, AuxVariable, not_, myrange_inclusive
# from src.encoding.binomial.common_binomial import binomial_at_most_k, binomial_at_least_k
import math


def _delete_dim(x: list[int], d: int) -> list[int]:
	ret: list[int] = []
	for i in range(len(x)):
		if i == d - 1:
			continue
		ret.append(x[i])
	return ret


def _get_int_repr(x_list: list[int], p: list[int]) -> int:
	res: int = 0
	n = len(x_list)
	for i in myrange_inclusive(0, n - 1,):
		if i > 0:
			res = res * p[i - 1]
		res = res + (x_list[i])
	return res


class ProductEncoding(BaselineEncoding):
	class GetVariableProduct:
		def __init__(self, x: list[int], k: int, aux: AuxVariable):
			self._x = x
			self._n = len(x)
			self._k = k
			self._p: list[int] = [math.ceil(self._n ** (1 / (k + 1)))] * (k + 1)
			self._vars: list[list[int]] = []
			var_repr: set[int] = set()
			for i in myrange_inclusive(1, k + 2):
				li: list[int] = [1] * (k + 1)
				if i > 1:
					li[i - 2] = 2
				self._vars.append(li)
				var_repr.add(_get_int_repr(li, self._p))

			for i in myrange_inclusive(1, self._n + k + 2):
				if len(self._vars) >= self._n:
					break
				li: list[int] = []
				num = i
				for j in range(len(self._p)):
					li.append((num % self._p[j]) + 1)
					num //= self._p[j]
				li = li[::-1]
				int_repr: int = _get_int_repr(li, self._p)
				if int_repr in var_repr:
					continue
				var_repr.add(int_repr)
				self._vars.append(li)
			assert len(self._vars) == self._n

			self._a: list[dict[tuple, int]] = []
			# print(f"cur_base = {current_base}")
			for d in myrange_inclusive(1, k + 1):
				self._a.append({})
				for var in self._vars:
					var_d = tuple(_delete_dim(var, d))
					# print(f"var = {var}, d = {d}, var_d = {var_d}")
					if not (var_d in self._a[d - 1]):
						# print(f"hello {cur_len}")
						self._a[d - 1][var_d] = aux.get_new_variable()
				# print(f"cur_base = {current_base}")

		def get_x_repr(self, i: int) -> list[int]:
			return self._vars[i - 1]

		def get_all_a_dim(self, d: int) -> list[int]:
			ret: list[int] = list(self._a[d - 1].values())
			ret.sort()
			return ret

		def get_a(self, d: int, y: tuple):
			return self._a[d - 1][y]

		def x(self, i: int) -> int:
			"""
			i from 1 to n
			"""
			if not (1 <= i <= self._n):
				raise RuntimeError(f"product: i is {i} while n is {self._n}")
			return self._x[i - 1]

		def not_x(self, i: int) -> int:
			return not_(self.x(i))

	def __init__(self):
		self.g = None

	def encode_at_most_k(self, var: list[int], k: int, aux: AuxVariable, add_clause: AddClause):
		n = len(var)
		if n <= k + 1:
			return BinomialEncoding().encode_at_most_k(var, k, aux, add_clause)
		self.g = ProductEncoding.GetVariableProduct(var, k, aux)
		for d in myrange_inclusive(1, k + 1):
			for i in myrange_inclusive(1, n):
				x_list = self.g.get_x_repr(i)
				y = tuple(_delete_dim(x_list, d))
				var_a = self.g.get_a(d, y)
				add_clause.add(self.g.not_x(i), var_a)
			all_a: list[int] = self.g.get_all_a_dim(d)
			ProductEncoding().encode_at_most_k(all_a, k, aux, add_clause)
