from sentry_config.criteria import *


class MustNotBeFive(SentryCriteria):
    def criteria(self, value):
        if value == 5:
            return "I must not be 5."
