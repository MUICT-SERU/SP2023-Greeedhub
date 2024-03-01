from termcolor import colored, cprint

import datetime
import random
import time

def getCurrentDate(format):
	return datetime.datetime.now().strftime(format)

hierarchy = 0

## TODO Put on a class and own file for easier readability throughout the code
def yprint(text, ptype='std'):
	global hierarchy

	if ptype == 'std':
		print(('\t'*hierarchy) + text)
	elif ptype == 'w':
		print(colored(('\t'*hierarchy) + 'Warning -> ' + text, 'yellow'))
	elif ptype == 'e':
		print(colored(('\t'*hierarchy) + 'Error -> ' + text, 'red'))
	elif ptype == 'i':
		print(colored(('\t'*hierarchy) + 'Info: ' + text, 'blue'))
	elif ptype == 's':
		print(colored(('\t'*hierarchy) + 'Success: ' + text, 'green'))
	elif ptype == 'st':
		print(colored(('\t'*hierarchy) + 'Task: ' + text, 'white', attrs=['bold']))
		hierarchy = hierarchy + 1
	elif ptype == 'dn':
		hierarchy = hierarchy - 1
		print(('\t'*hierarchy) + '----- Done: ' + text + ' -----\n')
	elif ptype == 'h':
		print(colored(('\t'*hierarchy) + text, 'magenta', attrs=['bold']))
	else:
		print(colored('Utils.yprint error! Bad usage!', 'red'))