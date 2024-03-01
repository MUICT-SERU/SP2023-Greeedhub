import logging
import logging.config

from spf import SanicPlugin
from sanic_apache_accesslogs import helpers
from sanic_apache_accesslogs import settings


class AccessLogPlugin(SanicPlugin):

    def __init__(self, *args, **kwargs):
        super(AccessLogPlugin, self).__init__(*args, **kwargs)
        # set the logger information
        self.logger_name = kwargs.get('logger_name',
                                      'sanic.plugin.accesslog')
        self.handler_name = kwargs.get('handler_name',
                                       'sanic.plugin.accesslog.handler')
        self.combined = kwargs.get('combined', settings.IS_COMBINED)
        self.configuration = helpers.build_logging_config(self.logger_name,
                                                          self.handler_name,
                                                          self.combined)

    @property
    def logger(self):
        logger = logging.getLogger(self.logger_name)
        return logger

    def on_registered(self, context, reg, *args, **kwargs):
        """Register the logger into the private context."""
        logging.config.dictConfig(self.configuration)
        context.logger = self.logger


# instantiate a plugin for SPF
my_plugin = instance = AccessLogPlugin()


@my_plugin.middleware(attach_to='response',
                      relative='post',
                      priority=9,  # lowest priority
                      with_context=True)
def print_access_log(request, response, context):
    """Log the entry."""
    logger = context['logger']
    if request is None:  # no request, do nothing
        return response

    extras = helpers.build_extras(request, response)
    # log the access
    logger.info('', extra=extras)
    return response
