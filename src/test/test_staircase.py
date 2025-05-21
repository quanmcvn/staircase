import sys
import os

from src.encoding.at_most_seq_card_encoding import AtMostSeqCard
from src.encoding.staircase_encoding import StaircaseEncoding
from src.include.common import myrange_inclusive, AuxVariable, AddClause


def tet(x: int, n: int) -> str:
	ret: str = ""
	for i in range(n):
		rm = x % 3
		if rm == 0:
			ret += '0'
		elif rm == 1:
			ret += '1'
		else:
			ret += 'q'
		x = x // 3
	return ret


def get_all_tet(n: int) -> list[str]:
	ret: list[str] = []
	for x in range(3 ** n):
		ret.append(tet(x, n))
	return ret


def get_all_bin(n: int) -> list[str]:
	ret: list[str] = []
	for x in range(2 ** n):
		ret.append(bin(x)[2:].zfill(n))
	return ret


def count_one(x: str) -> int:
	ret = 0
	for c in x:
		if c == '1':
			ret += 1
	return ret


def checking(calc: bool, ret: int):
	if calc:  # expect SAT
		print("expected SAT...", end='')
		if ret == 2560:
			print("ok")
		elif ret == 5120:  # UNSAT
			print("FAILED!!!")
			sys.exit(1)
		else:
			print(f"Unexpected {ret}")
			sys.exit(2)
	else:
		print("expected UNSAT...", end='')
		if ret == 2560:
			print("FAILED!!!")
			sys.exit(1)
		elif ret == 5120:  # UNSAT
			print("ok")
		else:
			print(f"Unexpected {ret}")
			sys.exit(2)


def input_str_to_formula(xs: str) -> list[list[int]]:
	x = []
	for i in range(len(xs)):
		if xs[i] == 'q':
			continue
		y = i + 1
		if xs[i] == '0':
			y = -y
		x.append([y])
	return x


def cl(x: list[int], file=None) -> None:
	for y in x:
		print(y, end=' ', file=file)
	print(0, file=file)


def eval_window_at_most(x: str, window_size: int, cap: int):
	now = 0
	for i in range(0, len(x)):
		if i >= window_size:
			if now > cap:
				return False
			now -= 1 if x[i - window_size] == '1' else 0
		now += 1 if x[i] == '1' else 0
	if now > cap:
		return False
	return True


def eval_window_at_least(x: str, window_size: int, cap: int):
	now = 0
	for i in range(0, len(x)):
		if i >= window_size:
			if now < cap:
				return False
			now -= 1 if x[i - window_size] == '1' else 0
		now += 1 if x[i] == '1' else 0
	if now < cap:
		return False
	return True


def eval_window_range(x: str, window_size: int, floor: int, cap: int):
	now = 0
	for i in range(0, len(x)):
		if i >= window_size:
			if not (floor <= now <= cap):
				return False
			now -= 1 if x[i - window_size] == '1' else 0
		now += 1 if x[i] == '1' else 0
	if not (floor <= now <= cap):
		return False
	return True


def test_single(forced_input: str, window_size: int, cap: int):
	formula = []
	n = len(forced_input)
	var = [_ for _ in myrange_inclusive(1, n)]
	encoder = AtMostSeqCard.SequentialCounter()
	aux = AuxVariable(n + 1)
	add_clause = AddClause(formula)
	encoder.encode_c_s(var, cap, window_size, count_one(forced_input), aux, add_clause)
	# added_var = StaircaseEncoding().staircase(var, window_size, cap, n + 1, formula)
	for line in input_str_to_formula(forced_input):
		formula.append(line)

	added_var = aux.get_total_added_var()

	filename = f"/tmp/amk/staircase/staircase_{n}_{window_size}_{cap}"
	with open(filename, "w") as file:
		print(f"p cnf {n + added_var} {len(formula)}", file=file)
		for line in formula:
			cl(line, file=file)

	calc = eval_window_at_most(forced_input, window_size, cap)
	print(f"{n} {forced_input} {window_size} {cap} {calc}")
	print(filename)
	ret = os.system(f"kissat -n -q {filename}")
	checking(calc, ret)


def test_single_at_least(forced_input: str, window_size: int, floor: int):
	formula = []
	n = len(forced_input)
	var = [_ for _ in myrange_inclusive(1, n)]
	aux = AuxVariable(n + 1)
	add_clause = AddClause(formula)
	StaircaseEncoding().encode_staircase_at_least(var, window_size, floor, aux, add_clause)
	for line in input_str_to_formula(forced_input):
		formula.append(line)

	added_var = aux.get_total_added_var()

	filename = f"/tmp/amk/staircase/staircase_{n}_{window_size}_{floor}"
	with open(filename, "w") as file:
		print(f"p cnf {n + added_var} {len(formula)}", file=file)
		for line in formula:
			cl(line, file=file)

	calc = eval_window_at_least(forced_input, window_size, floor)
	print(f"{n} {forced_input} {window_size} {floor} {calc}")
	print(filename)
	ret = os.system(f"kissat -q {filename}")
	checking(calc, ret)


def test_single_range(forced_input: str, window_size: int, floor: int, cap: int):
	formula = []
	n = len(forced_input)
	var = [_ for _ in myrange_inclusive(1, n)]
	encoder = StaircaseEncoding()
	aux = AuxVariable(n + 1)
	add_clause = AddClause(formula)
	encoder.encode_staircase_range(var, window_size, floor, cap, aux, add_clause)
	# added_var = StaircaseEncoding().staircase(var, window_size, cap, n + 1, formula)
	clause_real = len(formula)

	for line in input_str_to_formula(forced_input):
		formula.append(line)

	added_var = aux.get_total_added_var()
	w = window_size
	clause_calc = 0
	clause_calc += 8*n*cap - n + 2*w - 8*w*cap + 4*cap**2 + 8*cap + 2 - (4*n*cap**2 + 5*n*cap + 2*n) // w
	clause_calc += n * floor - w * floor + floor - (n * floor) // w
	u_e = min(cap, w - cap)
	clause_calc += (n//w - 1) * (u_e * (u_e + 1) + (w - 1 - u_e * 2) * u_e)
	filename = f"/tmp/amk/staircase/staircase_{n}_{window_size}_{floor}_{cap}"
	with open(filename, "w") as file:
		print(f"p cnf {n + added_var} {len(formula)}", file=file)
		for line in formula:
			cl(line, file=file)

	calc = eval_window_range(forced_input, window_size, floor, cap)
	print(f"{n} {forced_input} {window_size} {floor} {cap} {calc}")
	print(f"clause_real = {clause_real}, clause_calc = {clause_calc}")
	# if clause_real != clause_calc:
	# 	sys.exit(1)
	print(filename)
	ret = os.system(f"kissat -q {filename}")
	checking(calc, ret)


def test(n: int):
	xs = get_all_bin(n)
	for x in xs:
		for window_size in myrange_inclusive(2, n - 1):
			for floor in myrange_inclusive(1, window_size - 1):
				test_single_at_least(x, window_size, floor)
				# for cap in myrange_inclusive(floor + 1, window_size):
				# 	test_single_range(x, window_size, floor, cap)


def main():
	# os.system("mkdir /tmp/amk/staircase")
	# test(7)
	test_single_at_least('0010000', 4, 1)
	# test_single("0" * 35, 7, 3)
	# test_single("0" * 28, 6, 4, )
	# test_single("0" * 180, 18, 10)
	pass


if __name__ == '__main__':
	main()
