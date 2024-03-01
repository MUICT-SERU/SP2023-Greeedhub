#!/usr/bin/env python

""" Example dictConfig file.

    https://github.com/borntyping/python-colorlog

    https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig
    https://stackoverflow.com/questions/6729268/log-messages-appearing-twice-with-python-logging
    https://stackoverflow.com/questions/384076/how-can-i-color-python-logging-output
    https://stackoverflow.com/questions/33170207/how-to-reconfigure-a-logger-formatter-when-using-dictconfig
"""
import logging
import logging.config
import os

from colorlog import ColoredFormatter


class CustomColoredFormatter(ColoredFormatter):
    """ Customize a colored formatter.

        The following escape codes are made available for use in the format string:

        {color}, fg_{color}, bg_{color}: Foreground and background colors.
        bold, bold_{color}, fg_bold_{color}, bg_bold_{color}: Bold/bright colors.
        thin, thin_{color}, fg_thin_{color}: Thin colors (terminal dependent).
        reset: Clear all formatting (both foreground and background colors).

        The available color names are black, red, green, yellow, blue, purple, cyan and white.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_colors['CRITICAL'] = 'fg_bold_white,bg_bold_red'
        self.log_colors['DEBUG'] = 'fg_bold_purple'


ROOT = os.path.dirname(os.path.abspath(__file__))

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'color',
            'stream': 'ext://sys.stdout',
        },
        'console_debug': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'color',  # 'summary'
            'stream': 'ext://sys.stdout',
        },
        'null': {
            'class': 'logging.NullHandler',
            'level': 'NOTSET',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'filename': os.path.join(ROOT, 'test.log'),
            'mode': 'a',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
        'smtp': {
            'class': 'logging.handlers.SMTPHandler',
            'level': 'ERROR',
            'formatter': 'email',
            'mailhost': 'localhost',
            'fromaddr': 'logger@example.com',
            'toaddrs': ['developer1@example.com', 'developer2@example.com'],
            'subject': '[Project] Error encountered.',
            # 'credentials': ('username', 'password'),
        },
        'http': {
            'class': 'logging.handlers.HTTPHandler',
            'level': 'INFO',
            'host': 'localhost:5000',
            'url': '/logs',
            'method': 'POST',
        },
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(module)-17s line:%(lineno)-4d %(levelname)-8s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'color': {
            '()': CustomColoredFormatter,
            #'format': "[%(log_color)s%(levelname)-8s%(reset)s] %(blue)s%(message)s",
            'format': '%(asctime)s %(yellow)s%(module)-17s %(cyan)s line:%(lineno)-4d %(log_color)s%(levelname)-8s%(reset)s %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'summary': {
            'format': '%(asctime)s [%(levelname)-8s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
        'email': {
            'format': 'Timestamp: %(asctime)s\nModule: %(module)s\nLine: %(lineno)d\nMessage: %(message)s',
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['console', 'file'],  # 'http', 'smtp'],
            'level': 'INFO',
            'propagate': True,
        },
        'A': {
            'handlers': ['null'],
            'level': 'NOTSET',
            'propagate': False,
        },
        'B': {
            'handlers': ['console_debug'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'B.A': {
            'level': 'NOTSET',
            'propagate': True,
        }
    }
}


# https://docs.python.org/3/library/logging.html
#
# CRITICAL  50
# ERROR     40
# WARNING   30
# INFO      20
# DEBUG     10
# NOTSET     0

if __name__ == '__main__':

    logging.config.dictConfig(LOGGING_CONFIG)

    root = logging.getLogger()
    logger_A = logging.getLogger('A')
    logger_B = logging.getLogger('B')
    logger_C = logging.getLogger('C')
    logger_B_A = logging.getLogger('B.A')

    root.critical('root: Critical message.')
    root.error('root: Error message.')
    root.warning('root: Warning mesage.')
    root.info('root: Info message.')
    root.debug('root: Debug message.')

    try:
        raise ValueError('Error message.')
    except ValueError as e:
        root.exception('root: Exception message.')

    print('A - disabled, ignore')
    logger_A.critical('A: Critical message.')
    logger_A.error('A: Error message.')
    logger_A.warning('A: Warning mesage.')
    logger_A.info('A: Info message.')
    logger_A.debug('A: Debug message.')

    try:
        raise ValueError('Error message.')
    except ValueError as e:
        logger_A.exception('A: Exception message.')

    print('B.A')
    logger_B_A.critical('B.A: Critical message.')
    logger_B_A.error('B.A: Error message.')
    logger_B_A.warning('B.A: Warning mesage.')
    logger_B_A.info('B.A: Info message.')
    logger_B_A.debug('B.A: Debug message.')

    try:
        raise ValueError('Error message.')
    except ValueError as e:
        logger_B_A.exception('B.A: Exception message.')

    print('C - not setup with dictConfig')
    logger_C.critical('C: Critical message.')
    logger_C.error('C: Error message.')
    logger_C.warning('C: Warning mesage.')
    logger_C.info('C: Info message.')
    logger_C.debug('C: Debug message.')

    try:
        raise ValueError('Error message.')
    except ValueError as e:
        logger_C.exception('C: Exception message.')

    try:
        from logging_tree import printout
    except ImportError:
        print('Install logging_tree for a pretty visualization of your loggin tree.')
    else:
        printout()

