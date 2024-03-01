from unittest import TestCase
from unittest.mock import Mock

from unittest_additions import AdditionalAssertsMixin


class AdditionalAssertsMixinTestCase(TestCase):
    def setUp(self):
        class MixedTestCase(TestCase, AdditionalAssertsMixin):
            pass

        self.mixin = MixedTestCase()

    def test_assert_is_empty_raises_correct_exception_with_appropriate_message(self):
        containers = {'list': ['asdf'],
                        'tuple': ('asdf',),
                        'dict': {'asdf': 1},
                        'str': 'asdf',
                        'set': {'asdf'},}

        for k,v in containers.items():
            with self.assertRaisesRegex(TestCase.failureException, f'{k} is not empty.'):
                self.mixin.assertIsEmpty(v)

    def test_assert_is_empty_does_not_raise_when_empty(self):
        containers = {'list': list(),
                        'tuple': tuple(),
                        'dict': dict(),
                        'str': str(),
                        'set': set(),}

        try:
            for k,v in containers.items():
                self.mixin.assertIsEmpty(v)
        except TestCase.failureException as e:
            self.fail('assertIsEmpty raised failure when it should not have.')

    def test_assert_is_not_empty_raises_correct_exception_with_appropriate_message(self):
        containers = {'list': list(),
                        'tuple': tuple(),
                        'dict': dict(),
                        'str': str(),
                        'set': set(),}

        for k,v in containers.items():
            with self.assertRaisesRegex(TestCase.failureException, f'{k} is empty.'):
                self.mixin.assertIsNotEmpty(v)

    def test_assert_is_not_empty_does_not_raise_when_not_empty(self):
        containers = {'list': ['asdf'],
                        'tuple': ('asdf',),
                        'dict': {'asdf': 1},
                        'str': 'asdf',
                        'set': {'asdf'},}

        try:
            for k,v in containers.items():
                self.mixin.assertIsNotEmpty(v)
        except TestCase.failureException as e:
            self.fail('assertIsNotEmpty raised failure when it should not have.')