from typing import Callable, List

from anachronos.test.assertion import Assertion
from anachronos.test.registering_assertion_fixture import AssertionRegistry


class Test(object):

    def __init__(self, test_method: Callable, test_fixture: "TestCase"):
        self.test_fixture = test_fixture
        self.test_method = test_method
        self.name = test_method.__name__
        self.assertion_registry = AssertionRegistry()

    def run(self):
        self.test_fixture.setUp()
        self.assertion_registry.monkey_patch_test_fixture(self.test_fixture)

        self.test_method()
        self.test_fixture.tearDown()

    def get_assertions(self) -> List[Assertion]:
        return self.assertion_registry.assertions
