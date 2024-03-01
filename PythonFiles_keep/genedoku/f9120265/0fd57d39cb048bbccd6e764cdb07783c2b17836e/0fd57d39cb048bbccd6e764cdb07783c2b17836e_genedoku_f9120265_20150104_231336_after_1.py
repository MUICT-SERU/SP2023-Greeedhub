import random
import Matrix

class Chromosome:
	K = 2
	# 
	def __init__(self,m):
		random.seed()
		for i in range(len(m)):
			f = m[i]
			already = [x for x in f if x != 0]
			new = [x for x in range(len(m)) if x not in already]
			for j in range(len(f)):
				if f[j] == 0:
					add = random.choice(new)
					new.remove(add)
					f[j] = add
			m[i] = f

		# Transpose matrix (keeping list type on each column, tuples aren't useful on this approach)
		self._value_per_subgroup = Matrix.toggle_subgroup(m)
		self._value_per_columns = Matrix.transpose(m)
		self._value = m
		self._len = len(m)
		self._eval = None

	def evaluate(self):
		if self._eval is not None:
			return self._eval

		val = 0
		
		for i in range(self._len):
			unique_values = list(set(self._value[i]))
			val += self._len - len(unique_values)
			
			unique_values = list(set(self._value_per_columns[i]))
			val += self._len - len(unique_values)

			unique_values = list(set(self._value_per_subgroup[i]
			val += self._len - len(unique_values)

		self._eval = val
		return self._eval

	def adaptate(self,max_val):
		return max_val * Chromosome.K - self.evaluate()

	def __add__(self,other):
		m1 = self._add_by_subgroup(self,other)
		m2 = self._add_by_column(self,other) if random.choice([True,False]) else self._add_by_file(self,other)
		
		A = Chromosome (m1)
		B = Chromosome (m2)
		return A,B

	def _add_by_column(self,other):
		m_per_column = []
		for i in range(self._len):
			unique_values1 = list(set(self._value_per_column[i]))
			unique_values2 = list(set(other._value_per_column[i]))
			m_per_column.append(unique_values1 if unique_values1 > unique_values2 else unique_values2)
		
		return Matrix.transpose(m_per_column)

	def _add_by_file(self,other):
		m = []
		for i in range(self._len):
			unique_values1 = list(set(self._value[i]))
			unique_values2 = list(set(other._value[i]))
			m.append(unique_values1 if unique_values1 > unique_values2 else unique_values2)
		
		return m

	def _add_by_subgroup(self,other):
		m_per_subgroup = []
		for i in range(self._len):
			unique_values1 = list(set(self._value_per_subgroup[i]))
			unique_values2 = list(set(other._value_per_subgroup[i]))
			m_per_subgroup.append(unique_values1 if unique_values1 > unique_values2 else unique_values2)
		
		return Matrix.toggle_subgroup(m_per_subgroup)
