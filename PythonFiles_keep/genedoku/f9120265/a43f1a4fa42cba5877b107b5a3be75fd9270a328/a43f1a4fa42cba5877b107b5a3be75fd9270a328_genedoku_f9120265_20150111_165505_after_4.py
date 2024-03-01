import random
import math
import copy
import Matrix
from Chromosome import Chromosome

class SudokuChromosome(Chromosome):
	K = 1.5
	def __init__(self,m,lock_pos = True):
		random.seed()
		self.locked_pos = []
		self._value = copy.deepcopy(m)
		for i in range(len(self._value)):
			f = self._value[i]
			already = [x for x in f if x != 0]
			new = [x for x in range(1,len(self._value)+1) if x not in already]
			for j in range(len(f)):
				if f[j] == 0:
					add = random.choice(new)
					new.remove(add)
					f[j] = add
				elif lock_pos:
					self.locked_pos.append((i,j))

		# Transpose matrix (keeping list type on each column, tuples aren't useful on this approach)
		self._value_per_subgroup = Matrix.toggle_subgroups(self._value)
		self._value_per_columns = Matrix.transpose(self._value)
		self._len = len(self._value)
		self._eval = None

	def evaluate(self):
		if self._eval is not None:
			return self._eval

		val = 0
		
		for i in range(self._len):
			unique_values = Matrix.unique_values(self._value[i])
			val += self._len - len(unique_values)
			
			unique_values = Matrix.unique_values(self._value_per_columns[i])
			val += self._len - len(unique_values)

			unique_values = Matrix.unique_values(self._value_per_subgroup[i])
			val += self._len - len(unique_values)

		self._eval = val
		return self._eval

	def adaptate(self,max_val):
		return int(max_val * SudokuChromosome.K) - self.evaluate()

	def __add__(self,other):
		m1 = self._add_by_subgroup(other)
		m2 = random.choice([self._add_by_column,self._add_by_row])(other)
		
		A = SudokuChromosome (m1,False)
		A.locked_pos = self.locked_pos
		B = SudokuChromosome (m2, False)
		B.locked_pos = self.locked_pos
		return A,B

	def _add_by_column(self,other):
		m_per_column = []
		for i in range(self._len):
			unique_values1 = len(Matrix.unique_values(self._value_per_columns[i]))
			unique_values2 = len(Matrix.unique_values(other._value_per_columns[i]))
			m_per_column.append(self._value_per_columns[i] if unique_values1 > unique_values2 else other._value_per_columns[i])
		
		return Matrix.transpose(m_per_column)

	def _add_by_row(self,other):
		m = []
		for i in range(self._len):
			unique_values1 = len(Matrix.unique_values(self._value[i]))
			unique_values2 = len(Matrix.unique_values(other._value[i]))
			m.append(self._value[i] if unique_values1 > unique_values2 else other._value[i])
		
		return m

	def _add_by_subgroup(self,other):
		m_per_subgroup = []
		for i in range(self._len):
			unique_values1 = len(Matrix.unique_values(self._value_per_subgroup[i]))
			unique_values2 = len(Matrix.unique_values(other._value_per_subgroup[i]))
			m_per_subgroup.append(self._value_per_subgroup[i] if unique_values1 > unique_values2 else other._value_per_subgroup[i])
		
		return Matrix.toggle_subgroups(m_per_subgroup)

	def mutate(self):
		random.choice([self._switch_element,self._switch_per_subgroup,self._switch_per_file,self._switch_per_column])()

	def _switch_per_column(self):
		col_index = random.randrange(self._len)
		col = self._value[col_index]
		x = random.randrange(self._len)
		while (x,col_index) in self.locked_pos:
			x = random.randrange(self._len)
		y = random.randrange(self._len)
		while x == y or (y,col_index) in self.locked_pos:
			y = random.randrange(self._len)

		col[x],col[y] = col[y],col[x]

		self._value = Matrix.transpose(self._value_per_columns)
		self._value_per_subgroup = Matrix.toggle_subgroups(self._value)
	
	def _switch_per_file(self):
		row_index = random.randrange(self._len)
		row = self._value[row_index]
		x = random.randrange(self._len)
		while (row_index,x) in self.locked_pos:
			x = random.randrange(self._len)
		y = random.randrange(self._len)
		while x == y or (row_index,y) in self.locked_pos:
			y = random.randrange(self._len)

		row[x],row[y] = row[y],row[x]

		self._value_per_columns = Matrix.transpose(self._value)
		self._value_per_subgroup = Matrix.toggle_subgroups(self._value)

	def _switch_per_subgroup(self):
		l = int(math.sqrt(self._len))
		sub_index = random.randrange(self._len)
		sub = self._value_per_subgroup[sub_index]
		x = random.randrange(self._len)
		while Matrix.convert_positions_to_subgroups(sub_index,x,l) in self.locked_pos:
			x = random.randrange(self._len)
		y = random.randrange(self._len)
		while x == y or Matrix.convert_positions_to_subgroups(sub_index,y,l) in self.locked_pos:
			y = random.randrange(self._len)

		sub[x],sub[y] = sub[y],sub[x]

		self._value = Matrix.toggle_subgroups(self._value_per_subgroup)
		self._value_per_columns = Matrix.transpose(self._value)
	
	def _switch_element(self):
		opts = [self._switch_element_per_row,self._switch_element_per_column,self._switch_element_per_subgroup]
		for i in range(len(opts)):
			if opts[i]():
				break
	
	def _switch_element_per_row(self):
		selected = set()
		row_index = random.randrange(self._len)
		selected.update([row_index])
		row = self._value[row_index]
		already = Matrix.unique_values(row)
		while len(already) == 9 and not (len(already) == 9 and len(selected) == 9):
			row_index = random.randrange(self._len)
			selected.update([row_index])
			row = self._value[row_index]
			already = Matrix.unique_values(row)

		indexes = [x for x in range(len(row)) if row.count(row[x]) > 1]
		if len(indexes) == 0: return False
		x = random.choice(indexes)
		while (row_index,x) in self.locked_pos:
			x = random.choice(indexes)

		new = [v for v in range(1,self._len+1) if v not in already]
		if len(new) > 0:
			row[x] = random.choice(new)

			self._value_per_columns = Matrix.transpose(self._value)
			self._value_per_subgroup = Matrix.toggle_subgroups(self._value)
			return True
		
		return False
	
	def _switch_element_per_column(self):
		selected = set()
		row_index = random.randrange(self._len)
		selected.update([row_index])
		row = self._value_per_columns[row_index]
		already = Matrix.unique_values(row)
		while len(already) == 9 and not (len(already) == 9 and len(selected) == 9):
			row_index = random.randrange(self._len)
			selected.update([row_index])
			row = self._value_per_columns[row_index]
			already = Matrix.unique_values(row)

		indexes = [x for x in range(len(row)) if row.count(row[x]) > 1]
		if len(indexes) == 0: return False
		x = random.choice(indexes)
		while (x,row_index) in self.locked_pos:
			x = random.choice(indexes)

		new = [v for v in range(1,self._len+1) if v not in already]
		if len(new) > 0:
			row[x] = random.choice(new)

			self._value = Matrix.transpose(self._value_per_columns)
			self._value_per_subgroup = Matrix.toggle_subgroups(self._value)
			return True
		
		return False
	
	def _switch_element_per_subgroup(self):
		l = int(math.sqrt(self._len))
		selected = set()
		row_index = random.randrange(self._len)
		selected.update([row_index])
		row = self._value_per_subgroup[row_index]
		already = Matrix.unique_values(row)
		while len(already) == 9 and not (len(already) == 9 and len(selected) == 9):
			row_index = random.randrange(self._len)
			selected.update([row_index])
			row = self._value_per_subgroup[row_index]
			already = Matrix.unique_values(row)

		indexes = [x for x in range(len(row)) if row.count(row[x]) > 1]
		if len(indexes) == 0: return False
		x = random.choice(indexes)
		while Matrix.convert_positions_to_subgroups(row_index,x,l) in self.locked_pos:
			x = random.choice(indexes)

		new = [v for v in range(1,self._len+1) if v not in already]
		if len(new) > 0:
			row[x] = random.choice(new)

			self._value = Matrix.toggle_subgroups(self._value_per_subgroup)
			self._value_per_columns = Matrix.transpose(self._value)
			return True
		
		return False
