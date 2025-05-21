import os

import pypblib.pblib

from src.encoding.all import Encoder, EncodingType
from src.encoding.at_most_seq_card_encoding import AtMostSeqCard
from src.encoding.binomial_encoding import BinomialEncoding
from src.encoding.nsc_encoding import NSCEncoding
from src.encoding.pblib_encoding import PBLibEncoding
from src.encoding.staircase_encoding import StaircaseEncoding
from src.include.addline import write_full
from src.include.common import AuxVariable, AddClause, myrange_inclusive, not_


class CarSequencing:
	class ClassDesc:
		def __init__(self, index: int, demand: int, is_option_required: list[bool]):
			self.index = index
			self.demand = demand
			self.is_option_required = is_option_required

		def __str__(self):
			return f"{self.index} {self.demand} {[1 if x else 0 for x in self.is_option_required]}"

	class GetVariableCarSequencing:
		def __init__(self, num_cars: int, num_classes: int, num_options, aux: AuxVariable):
			self._num_cars = num_cars
			self._num_classes = num_classes
			self._num_options = num_options
			self._c: list[list[int]] = []
			for _i in range(self._num_cars):
				choices = []
				for _j in range(num_classes):
					choices.append(aux.get_new_variable())
				self._c.append(choices)
			self._o: list[list[int]] = []
			for _i in range(self._num_cars):
				options = []
				for _j in range(num_options):
					options.append(aux.get_new_variable())
				self._o.append(options)

		# def get_x(self, i: int) -> int:
		# 	"""
		# 	1 <= i <= num_cars
		# 	"""
		# 	if not (1 <= i <= self._num_cars):
		# 		raise RuntimeError(f"car_seq: x: i is {i} while num_cars is {self._num_cars}")
		# 	return self._cars[i - 1]

		def get_c(self, i: int, j: int) -> int:
			"""
			1 <= i <= num_cars
			1 <= j <= num_classes
			"""
			if not (1 <= i <= self._num_cars):
				raise RuntimeError(f"car_seq: c: i is {i} while num_cars is {self._num_cars}")
			if not (1 <= j <= self._num_classes):
				raise RuntimeError(f"car_seq: c: j is {j} while num_classes is {self._num_classes}")
			return self._c[i - 1][j - 1]

		def get_o(self, i: int, j: int) -> int:
			"""
			1 <= i <= num_cars
			1 <= j <= num_options
			"""
			if not (1 <= i <= self._num_cars):
				raise RuntimeError(f"car_seq: o: i is {i} while num_cars is {self._num_cars}")
			if not (1 <= j <= self._num_options):
				raise RuntimeError(f"car_seq: o: j is {j} while num_options is {self._num_classes}")
			return self._o[i - 1][j - 1]

	def __init__(self):
		self.g = None
		self.demand_constraint_option = 'pblib'
		self.capacity_constraint_option = 'staircase'
		self.domain_constraint_option = 'pblib'

	def _demand_constraint(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		# 1. Demand constraints
		# exactly sum c[i][j] == class_desc[j - 1].demand for j in [1, num_classes]
		if self.demand_constraint_option == 'pblib':
			for j in myrange_inclusive(1, num_classes):
				var = [self.g.get_c(i, j) for i in myrange_inclusive(1, num_cars)]
				encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BEST))
				encoder.encode_exactly_k(var, class_desc[j - 1].demand, aux, add_clause)
		elif self.demand_constraint_option == 'cpaior_c_c':
			for j in myrange_inclusive(1, num_classes):
				var = [self.g.get_c(i, j) for i in myrange_inclusive(1, num_cars)]
				encoder = AtMostSeqCard.SequentialCounter()
				encoder.encode_c_c(var, class_desc[j - 1].demand, aux, add_clause)
		else:
			raise RuntimeError(f"Unknown demand_constraint_option: {self.demand_constraint_option}")

	def _capacity_constraint(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):

		# 2. Capacity constraints
		# at_most_k sum o[i + k - 1][j] <= cap[j] for k in [1, window_size[k]] for j in [1, num_options] for i in [0, num_cars - window_size[j]]
		if self.capacity_constraint_option == 'staircase':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				stair_case_encoding = StaircaseEncoding()
				var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
				stair_case_encoding.encode_staircase(var_, window_size, cap, aux, add_clause)
		elif self.capacity_constraint_option == 'cpaior_c_a':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
				encoder = AtMostSeqCard.SequentialCounter()
				encoder.encode_c_a(var_, cap, window_size, aux, add_clause)
		elif self.capacity_constraint_option == 'cpaior_c_s':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				total_option = 0
				for car_class in class_desc:
					if car_class.is_option_required[j - 1]:
						total_option += car_class.demand
				var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
				encoder = AtMostSeqCard.SequentialCounter()
				encoder.encode_c_s(var_, cap, window_size, total_option, aux, add_clause)
		elif self.capacity_constraint_option == 'binomial':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
				for i in myrange_inclusive(0, num_cars - window_size):
					new_var = [var_[i + j_ - 1] for j_ in myrange_inclusive(1, window_size)]
					encoder = BinomialEncoding()
					encoder.encode_at_most_k(new_var, cap, aux, add_clause)
		elif self.capacity_constraint_option == 'nsc':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
				for i in myrange_inclusive(0, num_cars - window_size):
					new_var = [var_[i + j_ - 1] for j_ in myrange_inclusive(1, window_size)]
					encoder = NSCEncoding()
					encoder.encode_at_most_k(new_var, cap, aux, add_clause)
		elif self.capacity_constraint_option == 'staircase_binomial':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				if window_size <= 3:
					var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
					for i in myrange_inclusive(0, num_cars - window_size):
						new_var = [var_[i + j_ - 1] for j_ in myrange_inclusive(1, window_size)]
						encoder = BinomialEncoding()
						encoder.encode_at_most_k(new_var, cap, aux, add_clause)
				else:
					stair_case_encoding = StaircaseEncoding()
					var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
					stair_case_encoding.encode_staircase(var_, window_size, cap, aux, add_clause)
		elif self.capacity_constraint_option == 'cpaior_c_a_binomial':
			for j in myrange_inclusive(1, num_options):
				cap, window_size = option_cap[j - 1]
				if window_size <= 3:
					var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
					for i in myrange_inclusive(0, num_cars - window_size):
						new_var = [var_[i + j_ - 1] for j_ in myrange_inclusive(1, window_size)]
						encoder = BinomialEncoding()
						encoder.encode_at_most_k(new_var, cap, aux, add_clause)
				else:
					var_ = [self.g.get_o(i, j) for i in myrange_inclusive(1, num_cars)]
					encoder = AtMostSeqCard.SequentialCounter()
					encoder.encode_c_a(var_, cap, window_size, aux, add_clause)
		else:
			raise RuntimeError(f"Unknown capacity_constraint_option: {self.capacity_constraint_option}")

	def _channeling(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		# 3. Channeling
		for i in myrange_inclusive(1, num_cars):
			for l_ in myrange_inclusive(1, num_classes):
				for j in myrange_inclusive(1, num_options):
					if class_desc[l_ - 1].is_option_required[j - 1]:
						new_o = self.g.get_o(i, j)
					else:
						new_o = not_(self.g.get_o(i, j))
					add_clause.add(not_(self.g.get_c(i, l_)), new_o)

		# 3.2. Redundant for better propagation
		C: list[list[int]] = []
		for j in myrange_inclusive(1, num_options):
			c_temp = []
			for k in myrange_inclusive(1, num_classes):
				if class_desc[k - 1].is_option_required[j - 1]:
					c_temp.append(k)
			C.append(c_temp)

		for i in myrange_inclusive(1, num_cars):
			for j in myrange_inclusive(1, num_options):
				var: list[int] = [not_(self.g.get_o(i, j))]
				rhs = [self.g.get_c(i, l) for l in C[j - 1]]
				var.extend(rhs)
				add_clause.add_list(var)

	def _domain_constraint(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		# 4. Domain constraints
		# exactly c[i][j] == 1 for i in num_cars for j in num_classes
		if self.domain_constraint_option == 'pblib':
			for i in myrange_inclusive(1, num_cars):
				var = [self.g.get_c(i, j) for j in myrange_inclusive(1, num_classes)]
				encoder = PBLibEncoding(pypblib.pblib.PBConfig(pypblib.pblib.AMK_BEST))
				encoder.encode_exactly_k(var, 1, aux, add_clause)
		elif self.domain_constraint_option == 'cpaior_c_c':
			for i in myrange_inclusive(1, num_cars):
				var = [self.g.get_c(i, j) for j in myrange_inclusive(1, num_classes)]
				encoder = AtMostSeqCard.SequentialCounter()
				encoder.encode_c_c(var, 1, aux, add_clause)
		else:
			raise RuntimeError(f"Unknown domain_constraint_option: {self.domain_constraint_option}")

	def baseline(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		self.g = CarSequencing.GetVariableCarSequencing(num_cars, num_classes, num_options, aux)

		# 2
		self._capacity_constraint(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)
		# 3
		self._channeling(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)
		# 4
		self._domain_constraint(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)
		# 1
		self._demand_constraint(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_staircase(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):

		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'staircase'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_binomial(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):

		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'binomial'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_staircase_binomial(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):

		self.demand_constraint_option = 'pblib'
		self.capacity_constraint_option = 'staircase_binomial'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_nsc(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):

		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'nsc'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_cpaior_2014(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'cpaior_c_a'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)

	def encode_car_sequencing_cpaior_2014_binomial(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'cpaior_c_a_binomial'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)
	def encode_car_sequencing_cpaior_2014_c_s(self, num_cars: int, num_classes: int, num_options: int,
	                          option_cap: list[tuple[int, int]], class_desc: list[ClassDesc], aux: AuxVariable,
	                          add_clause: AddClause):
		self.demand_constraint_option = 'cpaior_c_c'
		self.capacity_constraint_option = 'cpaior_c_s'
		self.domain_constraint_option = 'cpaior_c_c'

		self.baseline(num_cars, num_classes, num_options, option_cap, class_desc, aux, add_clause)
