import inspect
from typing import Type, Dict, List, Tuple, Callable

from anachronos.test.assertion import Assertion
from anachronos.test.assertions.uncaught_exception_assertion import UncaughtExceptionAssertion
from anachronos.test.boot.test import Test


class TestSuite(object):

    def __init__(self, test_class: Type["anachronos.TestCase"]):
        self.test_fixture = test_class()
        self.assertions_by_test: Dict[str, List[Assertion]] = {}

    def run(self):
        self.test_fixture.setUpClass()

        for name, test_method in self.find_test_methods():
            test = Test(test_method, self.test_fixture)
            try:
                test.run()
                self.assertions_by_test[name] = test.get_assertions()
            except Exception as e:
                self.assertions_by_test[name] = [UncaughtExceptionAssertion(e)]

        self.test_fixture.tearDownClass()

    def find_test_methods(self) -> List[Tuple[str, Callable]]:
        return inspect.getmembers(self.test_fixture, lambda x: inspect.ismethod(x) and x.__name__.startswith("test"))
