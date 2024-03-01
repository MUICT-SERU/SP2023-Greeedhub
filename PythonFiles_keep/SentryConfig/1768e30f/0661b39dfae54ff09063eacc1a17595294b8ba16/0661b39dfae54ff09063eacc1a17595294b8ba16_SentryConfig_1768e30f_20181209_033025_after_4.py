""" This module contains the criteria checks for options in the config file. """

from sentry_config.criteria import *


class MustBeOne(SentryCriteria):
    def criteria(self, value):
        if value != 1:
            return "I must be equal to one!"


class LenMustBeFive(SentryCriteria):
    def criteria(self, value):
        if len(value) != 5:
            return "I must have a len of five!"
