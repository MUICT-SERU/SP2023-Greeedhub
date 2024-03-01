from abc import ABCMeta, abstractmethod

class Chromosome:
	__metaclass__ = ABCMeta

	@abstractmethod
	def evaluate(self): pass

	@abstractmethod
	def adaptate(self,max_val): pass

	@abstractmethod
	def __add__(self,other): pass

	@abstractmethod
	def mutate(self): pass
