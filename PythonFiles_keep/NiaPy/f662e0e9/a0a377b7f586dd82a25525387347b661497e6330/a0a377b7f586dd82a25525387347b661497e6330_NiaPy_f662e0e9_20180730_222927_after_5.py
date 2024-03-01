# encoding=utf8
# This is temporary fix to import module from parent folder
# It will be removed when package is published on PyPI
import sys
sys.path.append('../')
# End of fix

import random
import logging
import matplotlib.pyplot as plt
from NiaPy.algorithms.basic import FireflyAlgorithm
from NiaPy.benchmarks.utility import TaskConvPrint, TaskConvPlot

logging.basicConfig()
logger = logging.getLogger('examples')
logger.setLevel('INFO')

# For reproducive results
random.seed(1234)

global_vector = []


class MyBenchmark(object):
	def __init__(self):
		self.Lower = -11
		self.Upper = 11

	def function(self):
		def evaluate(D, sol):
			val = 0.0
			for i in range(D): val = val + sol[i] * sol[i]
			global_vector.append(val)
			return val
		return evaluate

def run_defult():
	for i in range(10):
		Algorithm = FireflyAlgorithm(D=10, NP=20, nFES=1000, alpha=0.5, betamin=0.2, gamma=1.0, benchmark=MyBenchmark())	
		Best = Algorithm.run()
		plt.plot(global_vector)
		global_vector = []
		logger.info(Best)
	plt.xlabel('Number of evaluations')
	plt.ylabel('Fitness function value')
	plt.title('Convergence plot')
	plt.show()

def simple_example(runs=10):
	for i in range(10):
		algo = FireflyAlgorithm(D=10, NP=20, nFES=1000, alpha=0.5, betamin=0.2, gamma=1.0, benchmark=MyBenchmark())	
		Best = algo.run()
		logger.info('%s %s' % (Best[0], Best[1]))

def logging_example():
	task = TaskConvPrint(D=50, nFES=50000, nGEN=50000, benchmark=MyBenchmark())
	algo = FireflyAlgorithm(NP=20, alpha=0.5, betamin=0.2, gamma=1.0, seed=None, task=task)
	best = algo.run()
	logger.info('%s %s' % (best[0], best[1]))

def plot_example():
	task = TaskConvPlot(D=50, nFES=50000, nGEN=10000, benchmark=MyBenchmark())
	algo = FireflyAlgorithm(NP=20, alpha=0.5, betamin=0.2, gamma=1.0, task=task)
	best = algo.run()
	logger.info('%s %s' % (best[0], best[1]))
	input('Press [enter] to continue')

logging_example()

# vim: tabstop=3 noexpandtab shiftwidth=3 softtabstop=3
