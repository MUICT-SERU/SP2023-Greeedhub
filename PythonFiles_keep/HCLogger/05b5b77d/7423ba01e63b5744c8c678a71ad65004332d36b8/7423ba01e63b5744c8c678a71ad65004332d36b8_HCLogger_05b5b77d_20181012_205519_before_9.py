import sys
import threading
sys.path.append("..")

from hprint import Logger

def feedback(l, tn):
	prefix = '[id={}]'.format(tn)
	l.info('{} Current hierarchy: {}'.format( prefix, Logger.get_hierarchy() ))
	l.warn('{} This is a very long warning message that will break into a multiline message to respect the hierarchy format.'.format(prefix))
	l.win('{} Feedback function finished!'.format(prefix))

def runner(logger, thread_number):
	logger.manual_log_func(feedback, logger, thread_number)

if __name__ == '__main__':
	for x in range(5):
		logger = Logger(filename='thread_file.log', verbose=False)
		t = threading.Thread(target=runner, args=(logger,x))
		t.start()
	logger.info('All threads were created!')
