import random
import sys
from Chromosome import Chromosome

class Evolution:
	def __init__(self,problem,initial_length,max_iter):
		self.problem = problem
		self.initial_length = initial_length
		self.max_iter = max_iter

		random.seed()

		self.chromosomes = []
		for i in range(self.initial_length):
			c = Chromosome(self.problem)
			self.chromosomes.append(c)
		self.evaluate()

	def start(self):
		i = 0
		while i < self.max_iter and self.max_val > 0:
			new_chrs = []
			genetic_pool = []

			for c in self.chromosomes:
				genetic_pool += [ c for i in range(c.adaptate(self.max_val)) ]

			for i in range(self.initial_length / 2):
				a = random.choice(genetic_pool)
				b = random.choice(genetic_pool)

				'''while b == a:
					b = random.choice(genetic_pool)'''

				new_a,new_b = a + b
				new_chrs += [new_a,new_b]

			self.chromosomes = new_chrs
			prev = self.better
			self.evaluate()
			if self.max_val < prev.evaluate():
				self.chromosomes[self.worse_index] = prev
				self.max_val = prev.evaluate()
			i+=1

	def evaluate(self):
		self.max_val = 0
		self.worse_value = sys.maxint
		self.better = None
		self.worse_index = 0
		self.vals = []
		for i in range(len(self.chromosomes)):
			c = self.chromosomes[i]
			v = c.evaluate()
			self.vals.append(v)
			
			if v >= self.max_val: 
				self.max_val = v
				self.better = c

			if v < self.worse_value:
				self.worse_index = i
				self.worse_value = v
