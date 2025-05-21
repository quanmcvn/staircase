import tempfile
import shutil

from src.include.common import cl


def clear_file(filename: str):
	with open(filename, "w"):
		pass


def add_p_cnf(num_var: int, num_clause: int, filename: str):
	add_line_at_beginning_of_file(f"p cnf {num_var} {num_clause}", filename)


def add_line_at_beginning_of_file(content: str, filename: str):
	with tempfile.NamedTemporaryFile(mode='wt', delete=False) as temp_file:
		with open(filename, "rt") as file:
			temp_file.write(content)
			temp_file.write('\n')
			shutil.copyfileobj(file, temp_file)
	shutil.move(temp_file.name, filename)


def write_full(n: int, formula: list[list[int]], filename: str):
	with open(filename, "w") as file:
		print(f"p cnf {n} {len(formula)}", file=file)
		for line in formula:
			cl(line, file)


def input_str_to_list(xs: str) -> list[int]:
	x = []
	for i in range(len(xs)):
		if xs[i] == '?':
			continue
		y = i + 1
		if xs[i] == '0':
			y = -y
		x.append(y)
	return x


def add_forced_input(xs: str, filename: str):
	with open(filename, "r") as file:
		line = file.readline()
		part = line.split(" ")
		num_var = int(part[2])
		num_clause = int(part[3])
		x = input_str_to_list(xs)
		n = len(x)
		num_clause += n
		with open(f"{filename[:-4]}_changed.cnf", "w") as changed_file:
			print(f"p cnf {num_var} {num_clause}", file=changed_file)
			shutil.copyfileobj(file, changed_file)
			for y in x:
				print(y, 0, file=changed_file)

