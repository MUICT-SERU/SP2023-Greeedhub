import time
import os
import inspect
from sys import stderr

ENV_DEBUG_MODE = 'VERBOSE'
ENV_ENABLE_TIME = 'ENABLE_TIME'
ENV_LINE_INFO_TO_STDERR = 'LINE_INFO_TO_STDERR'
def _getEnvOpt(envName, default=False):
    return default if envName not in os.environ else os.environ[envName]

ENABLE_DEBUG_MODE = _getEnvOpt(ENV_DEBUG_MODE)
ENABLE_TIME_PREFIX = _getEnvOpt(ENV_ENABLE_TIME)
ENABLE_LINE_INFO_TO_STDERR = _getEnvOpt(ENV_LINE_INFO_TO_STDERR)

timeformat = '[%m-%d %H:%M:%S]'

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

_fontColorForBGs = {
    'BG_BLACK': 'WHITE',
    'BG_RED': 'CYAN',
    'BG_GREEN': 'MAGENTA',
    'BG_YELLOW': 'BLUE',
    'BG_BLUE': 'YELLOW',
    'BG_MAGENTA': 'GREEN',
    'BG_CYAN': 'RED',
    'BG_WHITE': 'BLACK',
}

_CODE_DICT = {**_bgColors, **_effects, **_colors}

def getAllOptions():
    return _CODE_DICT.keys()

def getPrefix(codes):
    return '\x1b[' + ';'.join(codes) + 'm'

def _log(codes, *args, **kwargs):
    '''
    This is core function
    '''
    arguments = list(args)
    arguments.insert(0, getPrefix(codes))
    if ENABLE_TIME_PREFIX :
        arguments.insert(0, time.strftime(timeformat))

    arguments.append(END)
    print(*arguments, **kwargs)

# def cyan(*args):
#     _log([_colors['CYAN']], *args)
# def red(*args):
#     _log([_colors['RED']], *args)
# def italic(*args):
#     _log([_effects['ITALIC']], *args)

def _show(title, d):
    cyan(title)
    italic(', '.join(d.keys()))

def showOpts():
    '''
    BG_COLORS
    BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE
    EFFECTS
    RESET, BOLD, FAINT, ITALIC, UNDERLINE
    COLORS
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    '''
    _show('BG_COLORS', _bgColors)
    _show('EFFECTS', _effects)
    _show('COLORS', _colors)

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

def printLineInfo(*args, **kwargs):
    '''
    This function will print Filename/functionName:line at beggining.
    You can set environment variable LINE_INFO_TO_STDERR=1 to print this one to stderr
    '''
    previous_frame = inspect.currentframe().f_back
    (filename, line_number, function_name, _, _) = inspect.getframeinfo(previous_frame)
    lineInfo = filename + ':' + str(line_number)+ '/' + function_name
    if ENABLE_LINE_INFO_TO_STDERR:
        _log([_colors['RED']], lineInfo, *args, file=stderr)
    else:
        _log([_colors['RED']], lineInfo, *args)

def printStack():
    frames = inspect.getouterframes(inspect.currentframe().f_back)
    for f in frames:
        print(f.filename+':'+ str(f.lineno)+'/'+f.function, f.code_context[0].replace(' ',''), end='')

def debug(opts, *args):
    if ENABLE_DEBUG_MODE:
        log(opts, *args)

def oneOpt(opt):
    return lambda *args: log([opt], *args)

def bgColorShorthand(bgColor):
    def withBgColor(*args):
        try:
            log([bgColor, _fontColorForBGs[bgColor.upper()]], *args)
        except KeyError:
            _show('BG_COLORS', _bgColors)
    return withBgColor

black = oneOpt('black')
red = oneOpt('red')
green = oneOpt('green')
yellow = oneOpt('yellow')
blue = oneOpt('blue')
magenta = oneOpt('magenta')
cyan = oneOpt('cyan')
white = oneOpt('white')

bold = oneOpt('bold')
faint = oneOpt('faint')
italic = oneOpt('italic')
underline = oneOpt('underline')

bg_black = bgColorShorthand('bg_black')
bg_red = bgColorShorthand('bg_red')
bg_green = bgColorShorthand('bg_green')
bg_yellow = bgColorShorthand('bg_yellow')
bg_blue = bgColorShorthand('bg_blue')
bg_magenta = bgColorShorthand('bg_magenta')
bg_cyan = bgColorShorthand('bg_cyan')
bg_white = bgColorShorthand('bg_white')

_log([_colors['RED'], _effects['ITALIC'], _bgColors['BG_GREEN']],1,2,3)

red(3,2,1)

log(['red','Bg_Yellow', 'wrongOpt'], 3,4,5)
debug(['BG_CYAN'], 'this is debug msg')

printLineInfo()

def test():
    printLineInfo('1','2')
    printStack()
def a():
    test()
a()

green(123,'abc')
cyan('aa')

bg_yellow('log with bg yellow')