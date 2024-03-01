from anachronos.compat.jivago_streams import Stream
from anachronos.test.assertion import Assertion


class UnaryAssertion(Assertion):

    def __init__(self, item):
        self.item = item

    def run(self, anachronos: "Anachronos"):
        self._do_assertion(self.condition(anachronos.get_messages()), self.message())

    def message(self) -> str:
        raise NotImplementedError

    def condition(self, messages: list) -> bool:
        raise NotImplementedError


class NeverStoredAssertion(UnaryAssertion):

    def condition(self, messages: list) -> bool:
        return Stream(messages).noneMatch(lambda x: self.item == x.payload)

    def message(self) -> str:
        return f'Failed "NeverStored" assertion. {self.item} has been stored, but should not have.'


class NeverContainedAssertion(UnaryAssertion):

    def message(self) -> str:
        return f'Failed "NeverContains" assertion. {self.item} is contained in a message, but should not have.'

    def condition(self, messages: list) -> bool:
        return Stream(messages).noneMatch(lambda x: self.item in x.payload)


class ContainedAtLeastOnceAssertion(UnaryAssertion):

    def message(self) -> str:
        return f'Failed "ContainedAtLeastOnce" assertion. {self.item} is never contained in a message, but should have.'

    def condition(self, messages: list) -> bool:
        return Stream(messages).anyMatch(lambda x: self.item in x.payload)


class IsStoredAssertion(UnaryAssertion):

    def condition(self, messages: list):
        return Stream(messages).anyMatch(lambda x: self.item == x.payload)

    def message(self):
        return f'Failed "IsStored" assertion. Expected {self.item} to be stored at least once, but never was.'


class IsStoredOnlyOnce(UnaryAssertion):

    def condition(self, messages: list) -> bool:
        return Stream(messages).filter(lambda x: self.item == x.payload).count() == 1

    def message(self) -> str:
        return f'Failed "IsStoredOnlyOnce" assertion. Expected {self.item} to be stored once and only once, but wasn\'t.'
