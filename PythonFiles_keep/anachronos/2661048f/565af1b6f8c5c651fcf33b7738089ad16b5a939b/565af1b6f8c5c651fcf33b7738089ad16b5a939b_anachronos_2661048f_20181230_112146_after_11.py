from queue import Queue

from anachronos import anachronos
from anachronos.anachronos import AnachronosException
from anachronos.test.assertion import Assertion


class AssertionRunner(object):

    def __init__(self):
        self.assertions = Queue()

    def add(self, assertion: Assertion):
        self.assertions.put(assertion)

    def evaluate(self):
        failures = successes = 0
        for assertion in self.assertions.queue:
            try:
                assertion.run(anachronos)
                successes += 1
            except AnachronosException as e:
                failures += 1
                print(e)

        print(f"Ran {failures + successes} tests with {failures} errors.")
