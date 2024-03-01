from sanic.response import HTTPResponse

from .templates import LOGGER_DEFAULT, HANDLER_TEMPLATE, LOGGING_CONFIG_DEFAULTS


def build_extras(request, response):
    """Build the extra dict based on Apache's format."""
    extra = {
        'b': -1,
        'h': '-',
        'l': '-',
        'q': '',
        's': getattr(response, 'status', 0),
        'u': '-',
        'H': '-',
        'Referer': '-',
        'User-Agent': '-'
    }

    if isinstance(response, HTTPResponse):
        extra['b'] = len(response.body)

    if request.ip:
        extra['h'] = request.ip
    
    if request.remote_addr:  # get the real IP from the request
        extra['h'] = request.remote_addr

    if 'user' in request:  # TODO: support user deserialization
        extra['u'] = request.user

    extra['m'] = request.method
    extra['U'] = request.path
    if request.query_string:
        extra['q'] = '?{}'.format(request.query_string)
    extra['H'] = 'HTTP/{}'.format(request.version)

    if 'User-Agent' in request.headers:
        extra['User-Agent'] = request.headers['User-Agent']
    if 'Referer' in request.headers:
        extra['Referer'] = request.headers['Referer']

    return extra


def build_logging_configuration(logger_name,
                                handler_name,
                                combined=False,
                                template=LOGGING_CONFIG_DEFAULTS):
    """Build the logging configuration."""
    configuration['handlers'] = dict()
    handler = _build_handler(handler_name, combined)
    configuration.handlers[handler_name] = handler
    handlers = [handler_name]

    configuration['loggers'] = dict()
    logger = _build_logger(logger_name,
                           handlers)
    configuration.loggers[logger_name] = logger
    return configuration


# make an alias
build_logging_conf = build_logging_configuration


def _build_handler(name, combined=False, template=HANDLER_TEMPLATE):
    handler = template
    handler.formatter = 'combined' if combined else 'common'
    return handler


def _build_logger(name, handlers, template=LOGGER_DEFAULT):
    logger = template
    logger['qualname'] = name
    logger['handlers'] = handlers
    return logger
