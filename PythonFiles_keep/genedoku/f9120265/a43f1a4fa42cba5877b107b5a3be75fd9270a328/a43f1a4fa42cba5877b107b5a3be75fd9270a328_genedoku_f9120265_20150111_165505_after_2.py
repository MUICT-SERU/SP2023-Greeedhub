import random
import sys

class Evolution:
	def __init__(self,problem,ChromosomeClass,initial_length,max_iter):
		self.problem = problem
		self.initial_length = initial_length
		self.max_iter = max_iter

		random.seed()

		self.chromosomes = []
		for i in range(self.initial_length):
			c = ChromosomeClass(self.problem)
			self.chromosomes.append(c)
		self.evaluate()

	def start(self):
		self.gen = 0
		while self.gen < self.max_iter and self.better_value > 0:
			self.reproduce()
			
			self.mutate()

			prev = self.better
			self.evaluate()

			if self.better_value > prev.evaluate():
				self.chromosomes[self.worse_index] = prev
				self.better_value = prev.evaluate()
				self.better = prev
			self.gen+=1

		return self.better

	def mutate(self):
		for c in self.chromosomes:
			if random.randrange(len(self.chromosomes)/2) == 0:
				c.mutate()

	def reproduce(self):
		new_chrs = []
		genetic_pool = []

		for c in self.chromosomes:
			genetic_pool += [ c for i in range(c.adaptate(self.worse_value)) ]

		for i in range(len(self.chromosomes) / 2):
			a = random.choice(genetic_pool)
			b = random.choice(genetic_pool)

			i = 0
			while b == a and i < 50:
				b = random.choice(genetic_pool)
				i += 1
			new_a,new_b = a + b
			new_chrs += [new_a,new_b]

		self.chromosomes = new_chrs

	def evaluate(self):
		self.better_value = sys.maxint
		self.worse_value = 0
		self.better = None
		self.worse_index = 0
		self.vals = []
		for i in range(len(self.chromosomes)):
			c = self.chromosomes[i]
			v = c.evaluate()
			self.vals.append(v)
			
			if v <= self.better_value: 
				self.better_value = v
				self.better = c

			if v > self.worse_value:
				self.worse_index = i
				self.worse_value = v
