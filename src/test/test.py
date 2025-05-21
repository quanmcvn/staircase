import os
import sys
from src.include import addline
from src.include import function_template
from src.encoding.all import Encoder, str_to_type_enum
from src.include.common import myrange_inclusive
from src.include.function_template import add_basic, get_basic_function, get_basic_range_function


def run_notime(command: str):
	print(command)
	return os.system(command)


def get_cnt(x: str):
	ret = 0
	for c in x:
		if c == '1':
			ret += 1
	return ret


def get_cnt_qt(x: str):
	ret = 0
	for c in x:
		if c == '?':
			ret += 1
	return ret


def eval_alk(cnt: int, cnt_qt: int, k: int):
	return cnt + cnt_qt >= k


def eval_amk(cnt: int, _cnt_qt: int, k: int):
	return cnt <= k


def eval_ek(cnt: int, cnt_qt: int, k: int):
	return cnt <= k <= cnt + cnt_qt


def eval_range(cnt: int, cnt_qt: int, k: int, m: int):
	return k <= cnt + cnt_qt and cnt <= m


def try_eval(name: str, cnt: int, cnt_qt: int, k: int):
	if "at_least_k" in name or "hybrid" in name:
		return eval_alk(cnt, cnt_qt, k)
	if "at_most_k" in name:
		return eval_amk(cnt, cnt_qt, k)
	if "exactly_k" in name:
		return eval_ek(cnt, cnt_qt, k)
	print(f"??? {name}")
	sys.exit(3)


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


def tet(x: int, n: int) -> str:
	ret: str = ""
	for i in range(n):
		rm = x % 3
		if rm == 0:
			ret += '0'
		elif rm == 1:
			ret += '1'
		else:
			ret += '?'
		x = x // 3
	return ret


def get_all_tet(n: int) -> list[str]:
	ret: list[str] = []
	for x in range(3 ** n):
		ret.append(tet(x, n))
	return ret


def get_all_bin(n: int) -> list[str]:
	return [format(i, f'0{n}b') for i in range(2**n)]


def runall(n: int):
	xs: list[str] = get_all_bin(n)
	funcs = []
	for x in ["nsc_at_least_k"]:
		funcs.append(x)

	# for x in ["nsc_hybrid", "nsc_at_least_k", "sc_at_least_k", "binary_at_least_k", "commander_at_least_k", "product_at_least_k", "binomial_at_least_k", "pblib_bdd_at_least_k", "pblib_card_at_least_k"]:
	# 	funcs.append(x)
	# for x in ["nsc_at_most_k", "sc_at_most_k", "binary_at_most_k", "commander_at_most_k", "product_at_most_k", "binomial_at_most_k", "pblib_bdd_at_most_k", "pblib_card_at_most_k"]:
	# 	funcs.append(x)
	# for x in ["nsc_exactly_k", "sc_exactly_k", "binary_exactly_k", "commander_exactly_k", "product_exactly_k", "binomial_exactly_k", "pblib_bdd_exactly_k", "pblib_card_exactly_k"]:
	# 	funcs.append(x)
	# for x in ["at_most_seq_card_at_most_k"]:
	# 	funcs.append(x)
	# for x in ["nsc_at_most_k", "sc_at_most_k", "binary_at_most_k", "commander_at_most_k", "product_at_most_k", "binomial_at_most_k", "pblib_bdd_at_most_k", "pblib_card_at_most_k"]:
	# 	funcs.append(x)
	# for x in ["nsc_exactly_k", "sc_exactly_k", "binary_exactly_k", "commander_exactly_k", "product_exactly_k", "binomial_exactly_k", "pblib_bdd_exactly_k", "pblib_card_exactly_k"]:
	# 	funcs.append(x)
	# funcs = [add_basic_nsc_at_least_k, add_basic_nsc_at_most_k, add_basic_nsc_exactly_k]
	# funcs = [add_basic_binary_at_least_k, add_basic_binary_at_most_k, add_basic_binary_exactly_k]
	# funcs = [add_basic_binomial_at_least_k, add_basic_binomial_at_most_k]
	# funcs = [add_basic_commander_at_least_k, add_basic_commander_at_most_k, add_basic_commander_exactly_k]
	# funcs = [add_basic_pblib_at_least_k, add_basic_pblib_at_most_k, add_basic_pblib_exactly_k]
	# funcs = [add_basic_nsc_hybrid]
	# funcs = [add_basic_product_at_most_k, add_basic_product_at_least_k, add_basic_product_exactly_k]
	for name in funcs:
		func = get_basic_function(name)
		for k in myrange_inclusive(3, 3):
			filename = f"/tmp/amk/{name}_{n}_{k}.cnf"
			filename_changed = f"{filename[:-4]}_changed.cnf"
			total_var, total_clause = func(n, k, filename)
			for x in xs:
				addline.add_forced_input(x, filename)
				cnt = get_cnt(x)
				cnt_qt = get_cnt_qt(x)
				calc: bool = try_eval(name, cnt, cnt_qt, k)
				print(f"n = {n} k = {k}, cnt = {cnt}, cnt_qt = {cnt_qt}, eval = {calc}, {name}")
				print(f"x = {x}")
				total_added_var_calc = n * k - (k ** 2 - k) // 2 - 1
				total_clause_calc = 4 * n * k - n - 2 * k ** 2 - 2 + 1
				added_var = total_var - n
				print(f"total_added_var = {added_var}, total_added_var_calc = {total_added_var_calc}")
				print(f"total_clause = {total_clause}, total_clause_calc = {total_clause_calc}")
				# if added_var != total_added_var_calc:
				# 	sys.exit(1)
				# if total_clause != total_clause_calc:
				# 	sys.exit(1)
				ret = run_notime(f"kissat -n -q {filename_changed}")
				checking(calc, ret)


def runall2(n: int):
	xs: list[str] = get_all_bin(n)
	print(xs)
	# funcs = [add_basic_nsc_range, add_basic_sc_range]
	# funcs = [add_basic_binary_range]
	# funcs = [add_basic_commander_range]
	funcs = []
	for x in ["nsc_range"]:
		funcs.append(x)
	# for x in ["pblib_card_range"]:
	# 	funcs.append(x)
	for name in funcs:
		func = get_basic_range_function(name)
		for k in range(1, n):
			for m in range(k + 1, n + 1):
				filename = f"/tmp/amk/{name}_{n}_{k}_{m}.cnf"
				filename_changed = f"{filename[:-4]}_changed.cnf"
				func(n, k, m, filename)
				for x in xs:
					addline.add_forced_input(x, filename)
					cnt = get_cnt(x)
					cnt_qt = get_cnt_qt(x)
					calc: bool = eval_range(cnt, cnt_qt, k, m)
					print(f"x = {x} n = {n} k = {k}, m = {m}, cnt = {cnt}, cnt_qt = {cnt_qt}, eval = {calc}, {name}")
					ret = run_notime(f"kissat -n -q {filename_changed}")
					checking(calc, ret)


def main():
	# run_notime("mkdir -p /tmp/amk")
	# runall(10)
	runall(5)
	# runall2(3)
	# runall2(5)
	# runall2(8)
	# runall2(9)
	pass


if __name__ == '__main__':
	main()
