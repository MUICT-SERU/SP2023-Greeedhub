# encoding=utf8
# pylint: disable=mixed-indentation, trailing-whitespace, line-too-long, multiple-statements, attribute-defined-outside-init, logging-not-lazy, no-self-use, redefined-builtin, singleton-comparison, unused-argument, arguments-differ, no-else-return, bad-continuation
import logging
from scipy.spatial.distance import euclidean
from numpy import full, apply_along_axis, argmin, copy, sum, inf, fmax, pi, where
from NiaPy.algorithms.algorithm import Algorithm

logging.basicConfig()
logger = logging.getLogger('NiaPy.algorithms.basic')
logger.setLevel('INFO')

__all__ = ['GlowwormSwarmOptimization', 'GlowwormSwarmOptimizationV1', 'GlowwormSwarmOptimizationV2', 'GlowwormSwarmOptimizationV3']

class GlowwormSwarmOptimization(Algorithm):
	r"""Implementation of glowwarm swarm optimization.

	Algorithm:
		Glowwarm Swarm Optimization Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://www.springer.com/gp/book/9783319515946

	Reference paper:
		Kaipa, Krishnanand N., and Debasish Ghose. Glowworm swarm optimization: theory, algorithms, and applications. Vol. 698. Springer, 2017.

	Attributes:
		Name (list of str): List of strings represeinting algorithm name.
	"""
	Name = ['GlowwormSwarmOptimization', 'GSO']

	@staticmethod
	def typeParameters(): return {
			'n': lambda x: isinstance(x, int) and x > 0,
			'l0': lambda x: isinstance(x, (float, int)) and x > 0,
			'nt': lambda x: isinstance(x, (float, int)) and x > 0,
			'rho': lambda x: isinstance(x, float) and 0 < x < 1,
			'gamma': lambda x: isinstance(x, float) and 0 < x < 1,
			'beta': lambda x: isinstance(x, float) and x > 0,
			's': lambda x: isinstance(x, float) and x > 0
	}

	def setParameters(self, n=25, l0=5, nt=5, rho=0.4, gamma=0.6, beta=0.08, s=0.03, Distance=euclidean, **ukwargs):
		r"""Set the arguments of an algorithm.

		Arguments:
			n (int): Number of glowworms in population
			l0 (float): Initial luciferin quantity for each glowworm
			nt (float): --
			rs (float): Maximum sensing range
			rho (float): Luciferin decay constant
			gamma (float): Luciferin enhancement constant
			beta (float): --
			s (float): --
		"""
		self.n, self.l0, self.nt, self.rho, self.gamma, self.beta, self.s, self.Distance = n, l0, nt, rho, gamma, beta, s, Distance
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def randMove(self, i):
		r"""

		Args:
			i:

		Returns:

		"""
		j = i
		while i == j: j = self.randint(self.n)
		return j

	def getNeighbors(self, i, r, GS, L):
		r"""

		Args:
			i:
			r:
			GS:
			L:

		Returns:

		"""
		N = full(self.n, 0)
		for j, gw in enumerate(GS): N[j] = 1 if i != j and self.Distance(GS[i], gw) <= r and L[i] >= L[j] else 0
		return N

	def probabilityes(self, i, N, L):
		r"""

		Args:
			i:
			N:
			L:

		Returns:

		"""
		d, P = sum(L[where(N == 1)] - L[i]), full(self.n, .0)
		for j in range(self.n): P[i] = ((L[j] - L[i]) / d) if N[j] == 1 else 0
		return P

	def moveSelect(self, pb, i):
		r"""

		Args:
			pb:
			i:

		Returns:

		"""
		r, b_l, b_u = self.rand(), 0, 0
		for j in range(self.n):
			b_l, b_u = b_u, b_u + pb[i]
			if b_l < r < b_u: return j
		return self.randint(self.n)

	def calcLuciferin(self, L, GS_f):
		r"""

		Args:
			L:
			GS_f:

		Returns:

		"""
		return (1 - self.rho) * L + self.gamma * GS_f

	def rangeUpdate(self, R, N, rs):
		r"""

		Args:
			R:
			N:
			rs:

		Returns:

		"""
		return R + self.beta * (self.nt - sum(N))

	def initPopulation(self, task):
		r"""

		Args:
			task:

		Returns:

		"""
		rs = euclidean(full(task.D, 0), task.bRange)
		GS, L, R = self.uniform(task.Lower, task.Upper, [self.n, task.D]), full(self.n, self.l0), full(self.n, rs)
		GS_f = apply_along_axis(task.eval, 1, GS)
		return GS, GS_f, {'L':L, 'R':R, 'rs':rs}

	def runIteration(self, task, GS, GS_f, xb, fxb, L, R, rs, **dparams):
		r"""

		Args:
			task:
			GS:
			GS_f:
			xb:
			fxb:
			L:
			R:
			rs:
			**dparams:

		Returns:

		"""
		GSo, Ro = copy(GS), copy(R)
		L = self.calcLuciferin(L, GS_f)
		N = [self.getNeighbors(i, Ro[i], GSo, L) for i in range(self.n)]
		P = [self.probabilityes(i, N[i], L) for i in range(self.n)]
		j = [self.moveSelect(P[i], i) for i in range(self.n)]
		for i in range(self.n): GS[i] = task.repair(GSo[i] + self.s * ((GSo[j[i]] - GSo[i]) / (self.Distance(GSo[j[i]], GSo[i]) + 1e-31)), rnd=self.Rand)
		for i in range(self.n): R[i] = max(0, min(rs, self.rangeUpdate(Ro[i], N[i], rs)))
		GS_f = apply_along_axis(task.eval, 1, GS)
		return GS, GS_f, {'L':L, 'R':R, 'rs':rs}

class GlowwormSwarmOptimizationV1(GlowwormSwarmOptimization):
	r"""Implementation of glowwarm swarm optimization.

	Algorithm:
		Glowwarm Swarm Optimization Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://www.springer.com/gp/book/9783319515946

	Reference paper:
		Kaipa, Krishnanand N., and Debasish Ghose. Glowworm swarm optimization: theory, algorithms, and applications. Vol. 698. Springer, 2017.

	Attributes:
		Name (list of str): TODO
	"""
	Name = ['GlowwormSwarmOptimizationV1', 'GSOv1']

	def setParameters(self, **kwargs):
		self.__setParams(**kwargs)
		GlowwormSwarmOptimization.setParameters(self, **kwargs)

	def __setParams(self, alpha=0.2, **ukwargs):
		r"""Set the arguments of an algorithm.

		Arguments:
			alpha (float): --
		"""
		self.alpha = alpha
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def calcLuciferin(self, L, GS_f):
		r"""

		Args:
			L:
			GS_f:

		Returns:

		"""
		return fmax(0, (1 - self.rho) * L + self.gamma * GS_f)

	def rangeUpdate(self, R, N, rs):
		r"""

		Args:
			R:
			N:
			rs:

		Returns:

		"""
		return rs / (1 + self.beta * (sum(N) / (pi * rs ** 2)))

class GlowwormSwarmOptimizationV2(GlowwormSwarmOptimization):
	r"""Implementation of glowwarm swarm optimization.

	Algorithm:
		Glowwarm Swarm Optimization Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://www.springer.com/gp/book/9783319515946

	Reference paper:
		Kaipa, Krishnanand N., and Debasish Ghose. Glowworm swarm optimization: theory, algorithms, and applications. Vol. 698. Springer, 2017.

	Attributes:
		Name (list or str): TODO
	"""
	Name = ['GlowwormSwarmOptimizationV2', 'GSOv2']

	def setParameters(self, **kwargs):
		self.__setParams(alpha=kwargs.pop('alpha', 0.2), **kwargs)
		GlowwormSwarmOptimization.setParameters(self, **kwargs)

	def __setParams(self, alpha=0.2, **ukwargs):
		r"""Set the arguments of an algorithm.

		**Arguments:**

		beta1 {real} --

		s {real} --
		"""
		self.alpha = alpha
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def rangeUpdate(self, P, N, rs):
		r"""

		Args:
			P:
			N:
			rs:

		Returns:

		"""
		return self.alpha + (rs - self.alpha) / (1 + self.beta * sum(N))

class GlowwormSwarmOptimizationV3(GlowwormSwarmOptimization):
	r"""Implementation of glowwarm swarm optimization.

	Algorithm:
		Glowwarm Swarm Optimization Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://www.springer.com/gp/book/9783319515946

	Reference paper:
		Kaipa, Krishnanand N., and Debasish Ghose. Glowworm swarm optimization: theory, algorithms, and applications. Vol. 698. Springer, 2017.

	Attributes:
		Name (list of str): TODO
	"""
	Name = ['GlowwormSwarmOptimizationV3', 'GSOv3']

	def setParameters(self, **kwargs):
		self.__setParams(beta1=kwargs.pop('beta1', 0.2), **kwargs)
		GlowwormSwarmOptimization.setParameters(self, **kwargs)

	def __setParams(self, beta1=0.2, **ukwargs):
		r"""Set the arguments of an algorithm.

		**Arguments:**

		beta1 {real} --

		s {real} --
		"""
		self.beta1 = beta1
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def rangeUpdate(self, R, N, rs):
		r"""

		Args:
			R:
			N:
			rs:

		Returns:

		"""
		return R + (self.beta * sum(N)) if sum(N) < self.nt else (-self.beta1 * sum(N))

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
