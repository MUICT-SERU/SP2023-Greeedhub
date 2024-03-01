
print('\x1b[31;43m',123, 456,'\x1b[0m')
END = '\x1b[0m'
BgColors = {
    'BG_BLACK': '40',
    'BG_RED': '41',
    'BG_GREEN': '42',
    'BG_YELLOW': '43',
    'BG_BLUE': '44',
    'BG_MAGENTA': '45',
    'BG_CYAN': '46',
    'BG_WHITE': '47',
}

Effects = {
    'RESET': '0', #all attributes off
    'BOLD': '1', #Bold or increased intensity
    'FAINT': '2', #Faint (decreased intensity), Not widely supported.
    'ITALIC': '3', #Not widely supported. Sometimes treated as inverse.
    'UNDERLINE': '4',
};

Colors = {
	'BLACK': '30',
    'RED': '31',
    'GREEN': '32',
    'YELLOW': '33',
    'BLUE': '34',
    'MAGENTA': '35',
    'CYAN': '36',
    'WHITE': '37',
}

def getPrefix(codes):
	return '\x1b[' + ';'.join(codes) + 'm'

def red(*args):
	arguments = list(args)
	arguments.insert(0, getPrefix([Colors['RED']]))
	arguments.append(END)
	print(*arguments)

red(1,2,3)


