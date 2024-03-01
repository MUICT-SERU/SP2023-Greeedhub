from queue import Queue

from anachronos.assertion import Assertion


class AssertionRunner(object):

    def __init__(self):
        self.assertions = Queue()

    def add(self, assertion: Assertion):
        self.assertions.put(assertion)

    def evaluate(self):
        raise NotImplementedError
