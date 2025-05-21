from typing import Callable

from src.encoding.all import Encoder, str_to_type_enum
from src.include import addline


def add_basic(func: Callable[[list[int], int, int, list[list[int]]], int]) \
		-> Callable[[int, int, str], tuple[int, int]]:
	def add_basic_internal(n: int, k: int, filename: str) -> tuple[int, int]:
		num_var: int = n
		var: list[int] = [i for i in range(1, n + 1)]
		formula: list[list[int]] = []
		added_var = func(var, k, n + 1, formula)
		num_var += added_var
		num_clause = len(formula)
		addline.write_full(num_var, formula, filename)
		return num_var, num_clause

	return add_basic_internal


def add_basic_range(func: Callable[[list[int], int, int, int, list[list[int]]], int]) \
		-> Callable[[int, int, int, str], tuple[int, int]]:
	def add_basic_internal(n: int, k: int, m: int, filename: str) -> tuple[int, int]:
		num_var: int = n
		var: list[int] = [i for i in range(1, n + 1)]
		formula: list[list[int]] = []
		added_var = func(var, k, m, n + 1, formula)
		num_var += added_var
		num_clause = len(formula)
		addline.write_full(num_var, formula, filename)
		return num_var, num_clause

	return add_basic_internal


def get_basic_function(name: str) -> Callable[[int, int, str], tuple[int, int]]:
	return add_basic(Encoder(str_to_type_enum(name)).get_normal_encode_function(name))


def get_basic_range_function(name: str) -> Callable[[int, int, int, str], tuple[int, int]]:
	return add_basic_range(Encoder(str_to_type_enum(name)).get_range_encode_function())
