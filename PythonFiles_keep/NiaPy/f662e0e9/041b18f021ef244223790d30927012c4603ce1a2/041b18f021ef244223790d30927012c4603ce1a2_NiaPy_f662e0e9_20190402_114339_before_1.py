# encoding=utf8
# pylint: disable=mixed-indentation, line-too-long, singleton-comparison, multiple-statements, attribute-defined-outside-init, no-self-use, logging-not-lazy, unused-variable, arguments-differ, bad-continuation, redefined-builtin, unused-argument, consider-using-enumerate, expression-not-assigned
import logging
from scipy.spatial.distance import euclidean
from numpy import apply_along_axis, argsort, where, inf, random as rand, asarray, delete, sqrt, sum, unique, append
from NiaPy.algorithms.algorithm import Algorithm

logging.basicConfig()
logger = logging.getLogger('NiaPy.algorithms.basic')
logger.setLevel('INFO')

__all__ = ['CoralReefsOptimization']

def SexualCrossoverSimple(pop, p, task, rnd=rand, **kwargs):
	r"""TODO.

	Args:
		pop (array of array of (float or int): Current population
		p (float): Probability in range [0, 1]
		task (Task): Optimization task
		rnd (RandomState): Random generator
		**kwargs: Additional arguments

	Returns:
		Tuple[array of array of (float or int), array of float]:
			1. New population
			2. New population function/fitness values
	"""
	for i in range(len(pop) // 2): pop[i] = asarray([pop[i, d] if rnd.rand() < p else pop[i * 2, d] for d in range(task.D)])
	return pop, apply_along_axis(task.eval, 1, pop)

def BroodingSimple(pop, p, task, rnd=rand, **kwargs):
	r"""

	Args:
		pop (array of array of (float or int): Current population
		p (float): Probability in range [0, 1]
		task (Task): Optimization task
		rnd (RandomState): Random generator
		**kwargs: Additional arguments

	Returns:
		Tuple[array of array of (float or int), array of float]:
			1. New population
			2. New population function/fitness values
	"""
	for i in range(len(pop)): pop[i] = task.repair(asarray([pop[i, d] if rnd.rand() < p else task.Lower[d] + task.bRange[d] * rnd.rand() for d in range(task.D)]), rnd=rnd)
	return pop, apply_along_axis(task.eval, 1, pop)

def MoveCorals(pop, p, F, task, rnd=rand, **kwargs):
	r"""

	Args:
		pop (array of array of (float or int): Current population
		p (float): Probability in range [0, 1]
		F (float): Factor TODO
		task (Task): Optimization task
		rnd (RandomState): Random generator
		**kwargs: Additional arguments

	Returns:
		Tuple[array of array of (float or int), array of float]:
			1. New population
			2. New population function/fitness values
	"""
	for i in range(len(pop)): pop[i] = task.repair(asarray([pop[i, d] if rnd.rand() < p else pop[i, d] + F * rnd.rand() for d in range(task.D)]), rnd=rnd)
	return pop, apply_along_axis(task.eval, 1, pop)

class CoralReefsOptimization(Algorithm):
	r"""Implementation of Coral Reefs Optimization Algorithm.

	Algorithm:
		Coral Reefs Optimization Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference:
		S. Salcedo-Sanz, J. Del Ser, I. Landa-Torres, S. Gil-López, and J. A. Portilla-Figueras, “The Coral Reefs Optimization Algorithm: A Novel Metaheuristic for Efficiently Solving Optimization Problems,” The Scientific World Journal, vol. 2014, Article ID 739768, 15 pages, 2014. https://doi.org/10.1155/2014/739768.

	Attributes:
		Name (list of str): List of strings representing algorithm name
		N (int): Population size
		phi (int): TODO
		Fa (int): TODO
		Fb (int): Value in [0, 1] for Brooding size
		Fd (int): Value in [0, 1] for Depredation
		k (int): Nomber of trys for larva setting
		P_F (float): Mutation variable in [0, \inf]
		P_Cr(float): Crossover rate in [0, 1]
	"""
	Name = ['CoralReefsOptimization', 'CRO']
	N, phi, k = 25, 10, 25
	Fa, Fb, Fd = 0.5, 0.5, 0.3
	P_F, P_Cr = 0.36, 0.5

	@staticmethod
	def typeParameters():
		r"""TODO.

		Returns:
			dict:
				* N (func): TODO
				* phi (func): TODO
				* Fa (func): TODO
				* Fb (func): TODO
				* Fd (func): TODO
				* k (func): TODO
		"""
		return {
			# TODO funkcije za testiranje
			'N': False,
			'phi': False,
			'Fa': False,
			'Fb': False,
			'Fd': False,
			'k': False
		}

	def setParameters(self, N=25, phi=10, Fa=0.5, Fb=0.5, Fd=0.3, k=25, P_Cr=0.5, P_F=0.36, SexualCrossover=SexualCrossoverSimple, Brooding=BroodingSimple, Distance=euclidean, **ukwargs):
		r"""Set the parameters of the algorithm.

		Arguments:
			N (int): population size for population initialization
			phi (int): TODO
			Fa (float): TODO
			Fb (float): Value $\in [0, 1]$ for Brooding size
			Fd (float): Value $\in [0, 1]$ for Depredation
			k (int): Trys for larvae setting
			SexualCrossover (function): Crossover function
			P_Cr (float): Crossover rate $\in [0, 1]$
			Brooding (function): Brooding function
			P_F (float): Crossover rate $\in [0, 1]$
			Distance (function): Funciton for calculating distance between corals
		"""
		self.N, self.phi, self.Fa, self.Fb, self.Fd, self.k, self.P_Cr, self.P_F = N, phi, Fa, Fb, Fd, k, P_Cr, P_F
		self.SexualCrossover, self.Brooding, self.Distance = SexualCrossover, Brooding, Distance
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def initPopulation(self, task):
		r"""Initialize starting population.

		Args:
			task (Task): Optimization task

		Returns:
			Tuple[array of array of (float or int), array of float, dict]:
				1. Initialized population
				2. Initialized population fitness/function values
				3. dict:
					* Fa (int): TODO
					* Fb (int): TODO
					* Fd (int): TODO
		"""
		Fa, Fb, Fd = self.N * self.Fa, self.N * self.Fb, self.N * self.Fd
		if Fa % 2 != 0: Fa += 1
		Reef = task.Lower + self.rand([self.N, task.D]) * task.bRange
		Reef_f = apply_along_axis(task.eval, 1, Reef)
		return Reef, Reef_f, {'Fa':int(Fa), 'Fb':int(Fb), 'Fd':int(Fd)}

	def asexualReprodution(self, Reef, Reef_f, Fa, task):
		r"""Asexual reproduction of corals.

		Args:
			Reef (array of array of (float or int):
			Reef_f (array of float):
			Fa (int): Number of corals that are used in reproduction
			task (Task): Optimization task

		Returns:
			Tuple[array of array of (float or int), array of float]:
				1. New population
				2. New population fitness/funciton values

		See Also:
			* CoralReefsOptimization.setting
			* BroodingSimple
		"""
		I = argsort(Reef_f)[:Fa]
		Reefn, Reefn_f = self.Brooding(Reef[I], self.P_F, task, rnd=self.Rand)
		Reef, Reef_f = self.setting(Reef, Reef_f, Reefn, Reefn_f, task)
		return Reef, Reef_f

	def depredation(self, Reef, Reef_f, Fd):
		r"""TODO.

		Args:
			Reef (array of array of (float or int):
			Reef_f (array of (float or int):
			Fd (int): TODO

		Returns:
			Tuple[array of (float or int), float]:
				1. Best individual
				2. Best individual fitness/function value
		"""
		I = argsort(Reef_f)[::-1][:Fd]
		return delete(Reef, I), delete(Reef_f, I)

	def setting(self, X, X_f, Xn, Xn_f, task):
		r"""TODO.

		Args:
			X (array of array of (float or int):
			X_f (array of float):
			Xn (array of array of (float or int):
			Xn_f (array of float):
			task (Task): Optimization task

		Returns:
			Tuple[array of array of (float or int), array of float]:
				1. New population
				2. New population fitness/funciton values
		"""
		def update(A):
			D = asarray([sqrt(sum((A - e) ** 2, axis=1)) for e in Xn])
			I = unique(where(D < self.phi)[0])
			if I.any(): Xn[I], Xn_f[I] = MoveCorals(Xn[I], self.P_F, self.P_F, task, rnd=self.Rand)
		for i in range(self.k): update(X), update(Xn)
		D = asarray([sqrt(sum((X - e) ** 2, axis=1)) for e in Xn])
		I = unique(where(D >= self.phi)[0])
		return append(X, Xn[I], 0), append(X_f, Xn_f[I], 0)

	def runIteration(self, task, Reef, Reef_f, xb, fxb, Fa, Fb, Fd, **dparams):
		r"""Core function of Coral Reefs Optimization algorithm.

		Args:
			task (Task): Optiization task
			Reef (array of array of (float or int): Current population
			Reef_f (array of float): Current population fitness/function value
			xb (array of (float or int)): Current best solution
			fxb (float): Current best solution fitness/function value
			Fa (int): TODO
			Fb (int): TODO
			Fd (int): TODO
			**dparams: Additional arguments

		Returns:
			Tuple[array of array of (float or int), array of float, dict]:
				1. New population
				2. New population fitness/function values
				3. dict:
					* Fa (int): TODO
					* Fb (int): TODO
					* Fd (int): TODO
		"""
		I = self.Rand.choice(len(Reef), size=Fb, replace=False)
		Reefn_s, Reefn_s_f = self.SexualCrossover(Reef[I], self.P_Cr, task, rnd=self.Rand)
		Reefn_b, Reffn_b_f = self.Brooding(delete(Reef, I, 0), self.P_F, task, rnd=self.Rand)
		Reefn, Reefn_f = self.setting(Reef, Reef_f, append(Reefn_s, Reefn_b, 0), append(Reefn_s_f, Reffn_b_f, 0), task)
		Reef, Reef_f = self.asexualReprodution(Reefn, Reefn_f, Fa, task)
		if task.Iters % self.k == 0: Reef, Reef_f = self.depredation(Reef, Reef_f, Fd)
		return Reef, Reef_f, {'Fa':Fa, 'Fb':Fb, 'Fd':Fd}

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
