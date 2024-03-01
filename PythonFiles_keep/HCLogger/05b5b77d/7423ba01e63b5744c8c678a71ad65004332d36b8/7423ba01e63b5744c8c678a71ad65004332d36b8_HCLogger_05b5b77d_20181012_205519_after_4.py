# HCLogger demo
import sys
import time
import random

sys.path.append("..")

from hclogger import Logger

logger = Logger(filename='demo.log', verbose=False)

@logger.log_func
def main():
	if call_1():
		res = call_2()
		logger.debug('Highest value found: {}'.format(res))

	logger.warn('Slow network detected!')
	time.sleep(0.5)
	logger.error('Timeout reached! Aborting operation...')
	time.sleep(0.2)
	logger.win('Operation aborted successfully!')

@logger.log_func
def call_1():
	logger.info('Validating...')
	time.sleep(0.5)
	logger.win('Valid call 1')
	return True

@logger.log_func
def call_2():
	if True:
		return call_2_1()

def call_2_1():
	max_value = 0
	for x in range(20):
		value = round(random.random(), 3)
		max_value = max(max_value, value)
		if value > 0.9:		
			logger.high('Special value -{}- found!'.format(value))
		else:
			logger.info('Value -{}- found.'.format(value))
	return max_value

if __name__ == '__main__':
	main()