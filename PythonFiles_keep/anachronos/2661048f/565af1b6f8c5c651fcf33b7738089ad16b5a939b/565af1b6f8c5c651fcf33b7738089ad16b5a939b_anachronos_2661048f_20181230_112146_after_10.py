from anachronos import Anachronos
from anachronos.anachronos import AnachronosException
from anachronos.test.assertions.order_comparison import IsBeforeAssertion, IsAfterAssertion, \
    IsRoughlyAtTheSameTimeAssertion
from anachronos.test.assertions.unary import NeverStoredAssertion, NeverContainedAssertion


class Assertion(object):

    def run(self, anachronos: Anachronos):
        raise NotImplementedError

    def _do_assertion(self, boolean: bool, message: str):
        if not boolean:
            raise AnachronosException(message)


class AssertionFixture(object):

    def __init__(self, first_element):
        self.first_element = first_element

    def is_before(self, other) -> Assertion:
        return IsBeforeAssertion(self.first_element, other)

    def is_after(self, other) -> Assertion:
        return IsAfterAssertion(self.first_element, other)

    def is_at_same_time(self, other, delta_ms=1000) -> Assertion:
        return IsRoughlyAtTheSameTimeAssertion(self.first_element, other, delta_ms)

    def is_never_stored(self) -> Assertion:
        return NeverStoredAssertion(self.first_element)

    def is_never_contained(self) -> Assertion:
        return NeverContainedAssertion(self.first_element)


assertThat = AssertionFixture
