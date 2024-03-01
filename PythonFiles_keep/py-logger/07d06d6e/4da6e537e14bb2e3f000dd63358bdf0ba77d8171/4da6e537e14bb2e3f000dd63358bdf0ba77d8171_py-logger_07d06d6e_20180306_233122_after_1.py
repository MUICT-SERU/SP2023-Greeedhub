import time
import os
import inspect
from sys import stderr

ENV_DEBUG_MODE = 'VERBOSE'
ENV_ENABLE_TIME_PREFIX = 'ENABLE_TIME_PREFIX'
ENV_LINE_INFO_TO_STDERR = 'LINE_INFO_TO_STDERR'


def _get_env_opt(env_name, default=False):
    return default if env_name not in os.environ else os.environ[env_name]


ENABLE_DEBUG_MODE = _get_env_opt(ENV_DEBUG_MODE)
ENABLE_TIME_PREFIX = _get_env_opt(ENV_ENABLE_TIME_PREFIX)
ENABLE_LINE_INFO_TO_STDERR = _get_env_opt(ENV_LINE_INFO_TO_STDERR)

time_format = '[%m-%d %H:%M:%S]'

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
    'RESET': '0',  # all attributes off
    'BOLD': '1',  # Bold or increased intensity
    'FAINT': '2',  # Faint (decreased intensity), Not widely supported.
    'ITALIC': '3',  # Not widely supported. Sometimes treated as inverse.
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


def get_all_options():
    return _CODE_DICT.keys()


def _transform_codes(codes):
    return '\x1b[' + ';'.join(codes) + 'm'


def by_codes(codes, *args, **kwargs):
    """
    This is core function
    """
    arguments = list(args)
    arguments.insert(0, _transform_codes(codes))
    if ENABLE_TIME_PREFIX:
        arguments.insert(0, time.strftime(time_format))

    arguments.append(END)
    print(*arguments, **kwargs)


def _show(title, d):
    cyan(title)
    italic(', '.join(d.keys()))


def show_opts():
    """
    BG_COLORS
    BG_BLACK, BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE
    EFFECTS
    RESET, BOLD, FAINT, ITALIC, UNDERLINE
    COLORS
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
    """
    _show('BG_COLORS', _bgColors)
    _show('EFFECTS', _effects)
    _show('COLORS', _colors)


def _opts_to_codes(opts):
    opts_upper = [opt.upper() for opt in opts]
    try:
        codes = [_CODE_DICT[opt] for opt in opts_upper]
        return codes
    except KeyError:
        opts.insert(0, 'Unexpected options:')
        red(*opts)
        print('below are possible options(case insensitive)')
        show_opts()


def log(opts, *args):
    codes = _opts_to_codes(opts)
    if codes:
        by_codes(codes, *args)


def print_line_info(*args, **kwargs):
    """
    This function will print Filename/functionName:line at beggining.
    You can set environment variable LINE_INFO_TO_STDERR=1 to print this one to stderr
    """
    previous_frame = inspect.currentframe().f_back
    (filename, line_number, function_name, _, _) = inspect.getframeinfo(previous_frame)
    line_info = filename + ':' + str(line_number) + '/' + function_name
    if ENABLE_LINE_INFO_TO_STDERR:
        by_codes([_colors['RED']], line_info, *args, file=stderr)
    else:
        by_codes([_colors['RED']], line_info, *args)


def print_stack():
    frames = inspect.getouterframes(inspect.currentframe().f_back)
    for f in frames:
        print(f.filename + ':' + str(f.lineno) + '/' + f.function, f.code_context[0].replace(' ', ''), end='')


def debug(opts, *args):
    if ENABLE_DEBUG_MODE:
        log(opts, *args)


def _one_opt(opt):
    return lambda *args: log([opt], *args)


def _bg_color_shorthand(bg_color):
    def with_bg_color(*args):
        try:
            log([bg_color, _fontColorForBGs[bg_color.upper()]], *args)
        except KeyError:
            _show('BG_COLORS', _bgColors)

    return with_bg_color


def start(*opts):
    codes = _opts_to_codes(opts)
    print(_transform_codes(codes), end='')


def end():
    # Once start with bg color
    # Although using RESET to clear bgColor, but the spaces at the end still remain 1 line
    # Seems there a bug on osx?
    print(_transform_codes(['21', '22', '23', '24', _effects['RESET']]), end='')


black = _one_opt('black')
red = _one_opt('red')
green = _one_opt('green')
yellow = _one_opt('yellow')
blue = _one_opt('blue')
magenta = _one_opt('magenta')
cyan = _one_opt('cyan')
white = _one_opt('white')

bold = _one_opt('bold')
faint = _one_opt('faint')
italic = _one_opt('italic')
underline = _one_opt('underline')

bgBlack = _bg_color_shorthand('bg_black')
bgRed = _bg_color_shorthand('bg_red')
bgGreen = _bg_color_shorthand('bg_green')
bgYellow = _bg_color_shorthand('bg_yellow')
bgBlue = _bg_color_shorthand('bg_blue')
bgMagenta = _bg_color_shorthand('bg_magenta')
bgCyan = _bg_color_shorthand('bg_cyan')
bgWhite = _bg_color_shorthand('bg_white')

if __name__ == '__main__':
    by_codes([_colors['RED'], _effects['ITALIC'], _bgColors['BG_GREEN']], 1, 2, 3)

    log(['red', 'Bg_Yellow', 'wrongOpt'], 3, 4, 5)
    debug(['BG_CYAN'], 'this is debug msg')

    print_line_info()


    def test():
        print_line_info('1', '2')
        print_stack()


    def a():
        test()


    a()

    green(123, 'abc')
    cyan('aa')

    bgYellow('log with bg yellow')
    print('start', 'italic blue bg_green')

    start('italic', 'blue', 'bg_green')
    print('first', 'line')
    end()
    print('after', 'end()')
    print('after', 'end()')
