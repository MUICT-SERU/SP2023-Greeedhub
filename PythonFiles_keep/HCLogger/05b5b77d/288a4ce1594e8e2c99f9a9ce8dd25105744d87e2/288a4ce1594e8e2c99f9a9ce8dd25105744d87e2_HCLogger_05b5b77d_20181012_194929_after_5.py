# Test Python
import sys
import time
import termcolor

sys.path.append("..")

from termcolor import colored
from hprint import Logger

def colors():
	print(colored( 'This is a color', 'grey', attrs=[]))
	print(colored( 'This is a color', 'red', attrs=[]))
	print(colored( 'This is a color', 'green', attrs=[]))
	print(colored( 'This is a color', 'yellow', attrs=[]))
	print(colored( 'This is a color', 'blue', attrs=[]))
	print(colored( 'This is a color', 'magenta', attrs=[]))
	print(colored( 'This is a color', 'cyan', attrs=[]))
	print(colored( 'This is a color', 'white', attrs=[]))


def styles():
	print(colored( 'This is a color', 'yellow', attrs=['bold']))
	print(colored( 'This is a color', 'yellow', attrs=['underline']))
	print(colored( 'This is a color', 'yellow', attrs=['dark']))
	print(colored( 'This is a color', 'yellow', attrs=['concealed']))
	print(colored( 'This is a color', 'yellow', attrs=['reverse']))
	print(colored( 'This is a color', 'yellow', attrs=['blink']))

def feedback(l):
	l.info('This is a manual logged function')
	l.warn('This is a very long warning message that will break into a multiline message to respect the hierarchy format.')
	l.win('Manual logged function finished!')

if __name__ == '__main__':
	logger = Logger(filename='ftest_1.log', verbose=False)

	logger.error('Hello this is an error')
	logger.warn('Hello this is a warning')
	logger.high('Hello this is a highlight')
	logger.info('Hello this is an information')
	logger.debug('Hello this is an debug')
	logger.win('Hello this is an win')
	
	logger.manual_log_func(feedback, logger)

	@logger.log_func
	def op():
		logger.info('This is a decorated logged function')
		logger2 = Logger(filename="ftest_2.log", verbose=False)
		logger2.high('This is important message from Logger 2')

	op()