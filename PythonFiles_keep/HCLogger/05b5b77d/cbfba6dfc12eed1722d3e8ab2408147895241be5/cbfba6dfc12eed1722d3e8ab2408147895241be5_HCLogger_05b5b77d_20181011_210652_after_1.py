# Test Python
import time
import termcolor

from termcolor import colored
from hprint import Logger

def colors():

	print(clrd( 'This is a color', 'grey', attrs=[]))
	print(clrd( 'This is a color', 'red', attrs=[]))
	print(clrd( 'This is a color', 'green', attrs=[]))
	print(clrd( 'This is a color', 'yellow', attrs=[]))
	print(clrd( 'This is a color', 'blue', attrs=[]))
	print(clrd( 'This is a color', 'magenta', attrs=[]))
	print(clrd( 'This is a color', 'cyan', attrs=[]))
	print(clrd( 'This is a color', 'white', attrs=[]))


def styles():
	print(clrd( 'This is a color', 'yellow', attrs=['bold']))
	print(clrd( 'This is a color', 'yellow', attrs=['underline']))
	print(clrd( 'This is a color', 'yellow', attrs=['dark']))
	print(clrd( 'This is a color', 'yellow', attrs=['concealed']))
	print(clrd( 'This is a color', 'yellow', attrs=['reverse']))
	print(clrd( 'This is a color', 'yellow', attrs=['blink']))

def feedback(l):
	l.info('Starting feedback function...')
	time.sleep(1.55)
	for x in range(1,5):
		l.debug('This is a test: ' + str(x))
	l.warn('This is a very lno warning that will break with the indentation of the logger, it will also be interesting to fix tho.')
	l.info('Feedback function finished!')

if __name__ == '__main__':
	logger = Logger(filename='log1.log')

	logger.error('Hello this is an error')
	logger.warn('Hello this is a warning')
	logger.high('Hello this is a highlight')
	logger.info('Hello this is an information')
	logger.debug('Hello this is an debug')
	logger.win('Hello this is an win')
	logger.log_operation(feedback, logger)

	@logger.decorate_log
	def op(msg):
		logger2 = Logger(filename="log2.log")
		logger2.high('This is important message from Logger 2')
		logger.info('Writing message...')
		return msg + ' - She said'

	op('I love you')