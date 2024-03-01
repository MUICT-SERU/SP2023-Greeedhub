"""Helper module for the plugin."""
from sanic.response import HTTPResponse
from sanic_apache_accesslogs import templates


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

    # add the HTTP protocol version
    extra['H'] = 'HTTP/{}'.format(request.version)

    if 'User-Agent' in request.headers:
        extra['User-Agent'] = request.headers['User-Agent']
    if 'Referer' in request.headers:
        extra['Referer'] = request.headers['Referer']

    return extra


def build_logging_configuration(logger_name,
                                handler_name,
                                combined=False,
                                template=templates.LOGGING_CONFIG_DEFAULTS):
    """Build the logging configuration."""
    configuration = template
    # structure the handler(s)
    configuration['handlers'] = dict()
    handler = _build_handler(combined=combined)
    configuration['handlers'][handler_name] = handler
    handlers = [handler_name]

    # Structure the loggers
    configuration['loggers'] = dict()
    logger = _build_logger(logger_name,
                           handlers)
    configuration['loggers'][logger_name] = logger
    return configuration


# make an aliases
build_logging_config = build_logging_conf = build_logging_configuration


def _build_handler(combined, template=templates.HANDLER_TEMPLATE):
    """Build the handler for combined or common."""
    handler = template
    handler['formatter'] = 'combined' if combined else 'common'
    return handler


def _build_logger(name, handlers, template=templates.LOGGER_DEFAULT):
    """Build the logger."""
    logger = template
    logger['qualname'] = name
    logger['handlers'] = handlers

    return logger
