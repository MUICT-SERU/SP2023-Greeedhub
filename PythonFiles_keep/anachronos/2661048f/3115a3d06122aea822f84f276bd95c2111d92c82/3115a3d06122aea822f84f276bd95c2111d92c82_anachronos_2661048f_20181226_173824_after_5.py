from anachronos import Anachronos
from anachronos.anachronos import AnachronosException
from anachronos.assertions.order_comparison import IsBeforeAssertion, IsAfterAssertion, IsRoughlyAtTheSameTimeAssertion


class Assertion(object):

    def run(self, anachronos: Anachronos):
        raise NotImplementedError

    def _do_assertion(self, boolean: bool, message: str):
        if not boolean:
            raise AnachronosException(message)


class AssertionFixture(Assertion):

    def __init__(self, first_element):
        self.first_element = first_element

    def is_before(self, other) -> Assertion:
        return IsBeforeAssertion(self.first_element, other)

    def is_after(self, other) -> Assertion:
        return IsAfterAssertion(self.first_element, other)

    def is_at_same_time(self, other, delta_ms=1000) -> Assertion:
        return IsRoughlyAtTheSameTimeAssertion(self.first_element, other, delta_ms)

assertThat = AssertionFixture
