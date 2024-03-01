# encoding=utf8
# pylint: disable=mixed-indentation, trailing-whitespace, multiple-statements, attribute-defined-outside-init, logging-not-lazy, arguments-differ, line-too-long, unused-argument, bad-continuation
import logging
from numpy import apply_along_axis, argmin, argmax, log, exp, full
from NiaPy.algorithms.algorithm import Algorithm

logging.basicConfig()
logger = logging.getLogger('NiaPy.algorithms.basic')
logger.setLevel('INFO')

__all__ = ['HarmonySearch', 'HarmonySearchV1']

class HarmonySearch(Algorithm):
	r"""Implementation of harmony search algorithm.

	Algorithm:
		Harmony Search Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://link.springer.com/chapter/10.1007/978-3-642-00185-7_1

	Reference paper:
		Yang, Xin-She. "Harmony search as a metaheuristic algorithm." Music-inspired harmony search algorithm. Springer, Berlin, Heidelberg, 2009. 1-14.

	Attributes:
		Name (list of str): List of strings representing algorithm names
		r_accept (float): TODO
		r_pa (float): TODO
		b_range (float): TODO
	"""
	Name = ['HarmonySearch', 'HS']

	@staticmethod
	def typeParameters(): return {
			'HMS': lambda x: isinstance(x, int) and x > 0,
			'r_accept': lambda x: isinstance(x, float) and 0 < x < 1,
			'r_pa': lambda x: isinstance(x, float) and 0 < x < 1,
			'b_range': lambda x: isinstance(x, float) and x > 0
	}

	def setParameters(self, HMS=30, r_accept=0.7, r_pa=0.35, b_range=1.42, **ukwargs):
		r"""Set the arguments of the algorithm.

		Arguments:
			HMS (int): Number of harmonys in the memory
			r_accept (float): --
			r_pa (float): --
			b_range (float): --

		See Also:
			:func:`Algorithm.setParameters`
		"""
		Algorithm.setParameters(NP=HMS, **ukwargs)
		self.r_accept, self.r_pa, self.b_range = r_accept, r_pa, b_range
		if ukwargs: logger.info('Unused arguments: %s' % (ukwargs))

	def bw(self, task):
		r"""

		Args:
			task:

		Returns:

		"""
		return self.uniform(-1, 1) * self.b_range

	def adjustment(self, x, task):
		r"""

		Args:
			x:
			task:

		Returns:

		"""
		return x + self.bw(task)

	def improvize(self, HM, task):
		r"""

		Args:
			HM:
			task:

		Returns:

		"""
		H = full(task.D, .0)
		for i in range(task.D):
			r, j = self.rand(), self.randint(self.HMS)
			H[i] = HM[j, i] if r > self.r_accept else self.adjustment(HM[j, i], task) if r > self.r_pa else self.uniform(task.Lower[i], task.Upper[i])
		return H

	def initPopulation(self, task):
		r"""

		Args:
			task:

		Returns:
			Tuple[array of array of (float or int), array of float, dict]:
				1. New population
				2. New population fitness/function values
				3. Additional parameters

		See Also:
			:func:`Algorithm.initPopulation`
		"""
		return Algorithm.initPopulation(self, task)

	def runIteration(self, task, HM, HM_f, xb, fxb, **dparams):
		H = self.improvize(HM, task)
		H_f = task.eval(task.repair(H, self.Rand))
		iw = argmax(HM_f)
		if H_f <= HM_f[iw]: HM[iw], HM_f[iw] = H, H_f
		return HM, HM_f, {}

class HarmonySearchV1(HarmonySearch):
	r"""Implementation of harmony search algorithm.

	Algorithm:
		Harmony Search Algorithm

	Date:
		2018

	Authors:
		Klemen Berkovič

	License:
		MIT

	Reference URL:
		https://link.springer.com/chapter/10.1007/978-3-642-00185-7_1

	Reference paper:
		Yang, Xin-She. "Harmony search as a metaheuristic algorithm." Music-inspired harmony search algorithm. Springer, Berlin, Heidelberg, 2009. 1-14.

	Attributes:
		Name (list of str): List of strings representing algorithm name
		bw_min (float): TODO
		bw_max (float): TODO
	"""
	Name = ['HarmonySearchV1', 'HSv1']

	@staticmethod
	def typeParameters():
		d = HarmonySearch.typeParameters()
		del d['b_range']
		d['dw_min'] = lambda x: isinstance(x, (float, int))
		d['dw_max'] = lambda x: isinstance(x, (float, int))
		return d

	def setParameters(self, bw_min=1, bw_max=2, **kwargs):
		r"""Set the parameters of the algorithm.

		Arguments:
			bw_min (float): Minimal bandwidth
			bw_max (float): Maximal bandwidth

		See Also:
			:func:`HarmonySearch.setParameters`
		"""
		self.bw_min, self.bw_max = bw_min, bw_max
		HarmonySearch.setParameters(self, **kwargs)

	def bw(self, task):
		r"""

		Args:
			task:

		Returns:

		"""
		return self.bw_min * exp(log(self.bw_min / self.bw_max) * task.Iters / task.nGEN)

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
