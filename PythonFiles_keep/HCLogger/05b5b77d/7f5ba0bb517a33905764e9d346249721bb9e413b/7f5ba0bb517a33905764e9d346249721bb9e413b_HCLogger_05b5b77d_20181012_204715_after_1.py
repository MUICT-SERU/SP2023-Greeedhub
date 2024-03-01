import timeit
import datetime
import termcolor
import threading

from datetime import datetime
from termcolor import colored
from enum import Enum

class Color(Enum):
	GREY = 'grey'
	RED = 'red'
	GREEN = 'green'
	YELLOW = 'yellow'
	BLUE = 'blue'
	MAGENTA = 'magenta'
	CYAN = 'cyan'
	WHITE = 'white'

class Style(Enum):
	BOLD = ['bold']
	UNDERLINED = ['underlined']
	DARK = ['dark']
	BLINK = ['blink']
	REVERSE = ['reverse']
	CONCEALED = ['concealed']

class Logger(object):
	"""docstring for Logger"""

	# Shared variables
	_hierarchy_lock = threading.Lock()
	_hierarchy = 0

	# Add lock by filename to log to
	_filename_locks = {}

	# Colors
	colors = {}
	colors['default'] = Color.WHITE.value
	colors['err'] = Color.RED.value
	colors['warn'] = Color.YELLOW.value
	colors['info'] = Color.BLUE.value
	colors['debug'] = Color.CYAN.value
	colors['win'] = Color.GREEN.value
	colors['begin'] = Color.WHITE.value
	colors['end'] = Color.WHITE.value
	colors['high'] = Color.MAGENTA.value

	@classmethod
	def raise_hierarchy(cls):
		with cls._hierarchy_lock:
			cls._hierarchy += 1

	@classmethod
	def drop_hierarchy(cls):
		with cls._hierarchy_lock:
			cls._hierarchy -= 1

	@classmethod
	def get_hierarchy(cls):
		with cls._hierarchy_lock:
			return cls._hierarchy

	@classmethod
	def _get_file_lock(cls, filename):
		return cls._filename_locks.setdefault(filename, threading.Lock())

	def __init__(self, filename='hclogger.log', verbose=True):
		super(Logger, self).__init__()
		self.verbose = verbose
		self.filename = filename
		self.file_lock = Logger._get_file_lock(filename)
		self.max_line_len = 80

	def log_func(self, func):
		def wrapper(*args, **kwargs):
			return self.manual_log_func(func, *args, **kwargs)
		return wrapper

	def manual_log_func(self, func, *args, **kwargs):
		self.begin(func.__name__)
		start_time = timeit.default_timer()

		results = func(*args, **kwargs)

		elapsed_time = timeit.default_timer() - start_time
		self.end('<{}> [Took: {}s]'.format(func.__name__, round(elapsed_time,2)))
		return results

	def _print(self, header='', message='', raw_text=''):
		hierarchy_tabs = '\t'*Logger.get_hierarchy()
		date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S - ")
		self._write_log(hierarchy_tabs + date_str + raw_text)

		outputs = [date_str + header + message] if self.verbose else [header + message]

		while len(outputs[-1]) + len(hierarchy_tabs) > self.max_line_len:
			outputs += self._split_text(outputs.pop())
		[print('{}{}'.format(hierarchy_tabs, o)) for o in outputs]

	def _split_text(self, text):
		''' This function turns a text multiline while respecting the hierarchy format '''
		indexes = [i for i, v in enumerate(text) if v == ' ']
		index = self._find_index(0, indexes)
		return [text[:index], text[index+1:]]

	def _find_index(self, iindex, indexes):
		if iindex == len(indexes) - 1:
			return indexes[iindex]
		elif indexes[iindex] <= self.max_line_len:
			return self._find_index(iindex+1, indexes)
		else:
			return indexes[iindex-1]

	def _write_log(self, text):
		with self.file_lock:
			with open(self.filename, 'a+') as f:
				f.write(text + '\n')

	def begin(self, message):
		message = '<{}>'.format(message)
		header = 'Task: '
		self._print(colored(header, Logger.colors['begin'], attrs=Style.BOLD.value), message, header+message)
		Logger.raise_hierarchy()

	def end(self, message):
		Logger.drop_hierarchy()
		message = '{}\n'.format(message)
		header = 'Done processing '
		self._print(colored(header, Logger.colors['end']), message, header+message)

	def error(self, message):
		header = 'Error -> '
		self._print(colored(header, Logger.colors['err']), message, header+message)

	def warn(self, message):
		header = 'Warning -> '
		self._print(colored(header, Logger.colors['warn']), message, header+message)

	def debug(self, message):
		header = 'Debug: '
		self._print(colored(header, Logger.colors['debug']), message, header+message)

	def info(self, message):
		header = 'Info: '
		self._print(colored(header, Logger.colors['info']), message, header+message)

	def win(self, message):
		header = 'Success: '
		self._print(colored(header, Logger.colors['win']), message, header+message)

	def high(self, message):
		self._print(message=colored(message, Logger.colors['high'], attrs=Style.BOLD.value), raw_text=message)