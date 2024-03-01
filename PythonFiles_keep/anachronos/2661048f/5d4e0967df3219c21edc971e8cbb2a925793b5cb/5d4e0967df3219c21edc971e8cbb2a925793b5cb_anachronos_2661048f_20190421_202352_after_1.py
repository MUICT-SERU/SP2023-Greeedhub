from anachronos.test.assertion import Assertion
from anachronos.test.assertions.order_comparison import IsBeforeAssertion, IsAfterAssertion, \
    IsRoughlyAtTheSameTimeAssertion
from anachronos.test.assertions.schedule import OccursEveryXSeconds
from anachronos.test.assertions.unary import NeverStoredAssertion, NeverContainedAssertion, IsStoredAssertion, \
    ContainedAtLeastOnceAssertion, IsStoredOnlyOnce


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

    def is_stored(self) -> Assertion:
        return IsStoredAssertion(self.first_element)

    def is_stored_only_once(self) -> Assertion:
        return IsStoredOnlyOnce(self.first_element)

    def is_contained(self) -> Assertion:
        return ContainedAtLeastOnceAssertion(self.first_element)

    def occurs_every(self, seconds: int = 0, minutes: int = 0, hours: int = 0, tolerance_ms: int = 200):
        return OccursEveryXSeconds(self.first_element, seconds + minutes * 60 + hours * 3600, tolerance_ms=tolerance_ms)
