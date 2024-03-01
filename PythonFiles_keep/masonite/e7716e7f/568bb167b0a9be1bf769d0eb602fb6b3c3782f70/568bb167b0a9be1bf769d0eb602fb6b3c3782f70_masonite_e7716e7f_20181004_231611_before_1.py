""" Log Driver Module """

import logging
import os

from masonite.contracts.MailContract import MailContract
from masonite.drivers.BaseMailDriver import BaseMailDriver


class MailLogDriver(BaseMailDriver, MailContract):
    """Mail log driver
    """
    def __init__(self, MailConfig, View):
        super().__init__(MailConfig, View)

        handler = logging.FileHandler('{0}/{1}'.format(
            os.getcwd(),
            os.getenv('MAIL_LOGFILE', 'mail.log')
            ))
        self.logger = logging.getLogger(__name__)
        self.logger.handlers = []
        self.logger.propagate = False
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def send(self, message=None):
        """Prints the message in a log.

        Keyword Arguments:
            message {string} -- The message to be printed. (default: { None })

        Returns:
            None
        """

        if not message:
            message = self.message_body

        self.logger.info('***************************************')

        self.logger.info('To: {}'.format(self.to_address))
        self.logger.info('From: {0} <{1}>'.format(
            self.config.FROM['name'], self.config.FROM['address']))
        self.logger.info('Subject: {}'.format(self.message_subject))
        self.logger.info('Message: ')
        self.logger.info(message)

        self.logger.info('***************************************')
