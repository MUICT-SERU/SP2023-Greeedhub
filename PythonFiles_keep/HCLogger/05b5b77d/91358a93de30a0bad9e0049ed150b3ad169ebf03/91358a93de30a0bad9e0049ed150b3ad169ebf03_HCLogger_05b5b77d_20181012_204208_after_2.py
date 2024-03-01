# Test Python
import sys
import time
import termcolor

sys.path.append("..")

from termcolor import colored
from hprint import Logger

def feedback(l):
	l.info('This is a manual logged function')
	l.warn('This is a very long warning message that will break into a multiline message to respect the hierarchy format.')
	l.win('Manual logged function finished!')

if __name__ == '__main__':
	logger = Logger(filename='ftest_1.log', verbose=False)

	print('\n\n\nUsage: \n')

	logger.debug('logger.debug()')
	logger.info('logger.info()')
	logger.high('logger.high()')
	logger.warn('logger.warn()')
	logger.error('logger.error()')
	logger.win('logger.win()')

	print('\n')
	
	logger.manual_log_func(feedback, logger)

	@logger.log_func
	def op():
		logger.info('This is a decorated logged function')
		logger2 = Logger(filename="ftest_2.log", verbose=False)
		logger2.high('This is important message from Logger 2')

	op()