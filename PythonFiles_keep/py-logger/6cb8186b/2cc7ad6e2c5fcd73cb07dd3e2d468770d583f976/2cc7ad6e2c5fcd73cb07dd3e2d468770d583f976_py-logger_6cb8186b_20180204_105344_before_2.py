END = '\x1b[0m'
_bgColors = {
    'BG_BLACK': '40',
    'BG_RED': '41',
    'BG_GREEN': '42',
    'BG_YELLOW': '43',
    'BG_BLUE': '44',
    'BG_MAGENTA': '45',
    'BG_CYAN': '46',
    'BG_WHITE': '47',
}

_effects = {
    'RESET': '0', #all attributes off
    'BOLD': '1', #Bold or increased intensity
    'FAINT': '2', #Faint (decreased intensity), Not widely supported.
    'ITALIC': '3', #Not widely supported. Sometimes treated as inverse.
    'UNDERLINE': '4',
}

_colors = {
	'BLACK': '30',
    'RED': '31',
    'GREEN': '32',
    'YELLOW': '33',
    'BLUE': '34',
    'MAGENTA': '35',
    'CYAN': '36',
    'WHITE': '37',
}

_CODE_DICT = {**_bgColors, **_effects, **_colors}

def getPrefix(codes):
	return '\x1b[' + ';'.join(codes) + 'm'

def _log(codes, *args):
	'''
	This is core function
	'''
	arguments = list(args)
	arguments.insert(0, getPrefix(codes))
	arguments.append(END)
	print(*arguments)

def cyan(*args):
	_log([_colors['CYAN']], *args)
def red(*args):
	_log([_colors['RED']], *args)
def italic(*args):
	_log([_effects['ITALIC']], *args)

def showOpts():
    def show(title, d):
        cyan(title)
        italic(', '.join(d.keys()))
    show('BG_COLORS', _bgColors)
    show('EFFECTS', _effects)
    show('COLORS', _colors)

def log(opts, *args):
    optsUpper = [opt.upper() for opt in opts ]
    try:
        codes = [_CODE_DICT[opt] for opt in optsUpper]
        _log(codes, *args)
    except KeyError:
        opts.insert(0,'Unexpected options:')
        red(*opts)
        print('below are possible options(case insensitive)')
        showOpts()


_log([_colors['RED'], _effects['ITALIC'], _bgColors['BG_GREEN']],1,2,3)

red(3,2,1)

log(['red','Bg_Yellow', 'wrongOpt'], 3,4,5)