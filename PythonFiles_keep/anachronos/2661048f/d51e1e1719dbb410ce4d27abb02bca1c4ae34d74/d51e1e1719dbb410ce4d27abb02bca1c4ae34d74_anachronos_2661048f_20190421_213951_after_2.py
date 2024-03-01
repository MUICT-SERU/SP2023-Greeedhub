from datetime import timedelta
from typing import Callable

from anachronos.compat.jivago_streams import Stream
from anachronos.test.assertion import Assertion


class OrderComparisonAssertion(Assertion):
    def __init__(self, first, second, comparison_function: Callable, message: str):
        self.message = message
        self.comparison_function = comparison_function
        self.first = first
        self.second = second

    def run(self, anachronos: "Anachronos"):
        messages = Stream(anachronos.get_messages()).map(lambda x: x.payload).toList()
        first_index = messages.index(self.first)
        second_index = messages.index(self.second)

        condition = self.comparison_function(first_index, second_index)

        self._do_assertion(condition, self.message)


class IsBeforeAssertion(OrderComparisonAssertion):

    def __init__(self, first, second):
        super().__init__(first, second, lambda f, s: f < s,
                         f'Failed "IsBefore" assertion. Expected "{first}" before "{second}".')


class IsAfterAssertion(OrderComparisonAssertion):

    def __init__(self, first, second):
        super().__init__(first, second, lambda f, s: f > s,
                         f'Failed "IsAfter" assertion. Expected "{first}" after "{second}".')


class IsRoughlyAtTheSameTimeAssertion(Assertion):

    def __init__(self, first, second, delta_ms=1000):
        self.first = first
        self.second = second
        self.delta_ms = delta_ms

    def run(self, anachronos: "Anachronos"):
        messages = anachronos.get_messages()

        first, second = Stream.of(self.first, self.second) \
            .map(lambda x: Stream(messages).firstMatch(lambda m: m.payload == x)) \
            .toTuple()

        self._do_assertion(first.time - timedelta(milliseconds=self.delta_ms) <= second.time <= first.time + timedelta(
            milliseconds=self.delta_ms),
                           f'Faild "IsRoughlyAtTheSameTime" assertion. Expected {self.first} within {self.delta_ms}ms of {self.second}.')
