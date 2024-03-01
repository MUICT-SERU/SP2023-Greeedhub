import sys
import logging

from spf import SanicPlugin


LOGGER_DEFAULT = {
    'level': 'INFO',
    'handlers': [],
    'propagate': True,
    'qualname': ''
}


HANDLER_TEMPLATE = {
    'class': 'logging.StreamHandler',
    'formatter': '',
    'stream': sys.stdout
}


LOGGING_CONFIG_DEFAULTS = dict(
    version=1,
    disable_existing_loggers=False,
    formatters={
        'common': {
            'format': '%(h)s %(l)s %(u)s %(asctime)s '
                      + '"%(m)s %(U)s%(q)s %(H)s" %(s)d %(b)d',
            'datefmt': '[%Y-%m-%d %H:%M:%S%z]',
            'class': 'logging.Formatter'
        },
        'combined': {
            'format': '%(h)s %(l)s %(u)s %(asctime)s '
                      + '"%(m)s %(U)s%(q)s %(H)s" %(s)d %(b)d'
                      + '"%(Referer)s" "%(User-Agent)s"',
            'datefmt': '[%Y-%m-%d %H:%M:%S%z]',
            'class': 'logging.Formatter'
        }
    }
)


class AccessLogPlugin(SanicPlugin):

    def __init__(self, logger_name='sanic.plugin.accesslog',
                 combined=False, *args, **kwargs):
        super(AccessLogPlugin, self).__init__(*args, **kwargs)
        # set the logger information
        self.logger_name = logger_name
        self.handler_name = 'sanic.plugin.accesslog.handler'
        self.combined = combined

        self._set_configuration(LOGGING_CONFIG_DEFAULTS)

    def _set_configuration(self, configuration):
        configuration['handlers'] = dict()

        # get the name
        handler_name = self.handler_name
        handler = self._build_handler(handler_name)
        configuration.handlers[handler_name] = handler
        handlers = [handler_name]

        configuration['loggers'] = dict()

        # get the name
        logger_name = self.logger_name
        logger = self._build_logger(logger_name,
                                    handlers)
        configuration.loggers[logger_name] = logger

        logging.config.dictConfig(configuration)

    def _build_handler(self, name, template=HANDLER_TEMPLATE):
        handler = template
        handler.formatter = 'combined' if self.combined else 'common'
        return handler

    def _build_logger(self, name, handlers, template=LOGGER_DEFAULT):
        logger = template
        logger['qualname'] = name
        logger['handlers'] = handlers

        return logger

    @property
    def logger(self):
        logger = logging.getLogger(self.logger_name)
        return logger

    def on_registered(self, context, reg, *args, **kwargs):
        """Register the logger into the private context."""
        context.logger = self.logger


accesslog_plugin = AccessLogPlugin()
