import logging

from spf import SanicPlugin
from sanic_access_logs.helpers import build_extras, build_logging_config


class AccessLogPlugin(SanicPlugin):

    def __init__(self,
                 logger_name='sanic.plugin.accesslog',
                 handler_name='sanic.plugin.accesslog.handler',
                 combined=False,
                 *args, **kwargs):
        super(AccessLogPlugin, self).__init__(*args, **kwargs)
        # set the logger information
        self.logger_name = logger_name
        self.handler_name = handler_name
        self.combined = combined
        self.configuration = build_logging_config(logger_name,
                                                  handler_name,
                                                  combined)

    @property
    def logger(self):
        logger = logging.getLogger(self.logger_name)
        return logger

    def on_registered(self, context, reg, *args, **kwargs):
        """Register the logger into the private context."""
        context.logger = self.logger


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

    extras = build_extras(request, response)

    # log the access
    logger.info('', extra=extra)
    return response
