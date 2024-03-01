from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.utils import iteritems

from unittest import TestCase

from fixtureupper.register import UpperRegister

class TestModelFixtureUpper(TestCase):
    def setUp(self):
        self.ModelFixtureUpper = UpperRegister('Model')

    def test_sorted_by_generated_order(self):
        self.ModelFixtureUpper.generated_field_order = ['a', 'z', 'c', 'b', 'd']
        m_fu = self.ModelFixtureUpper()
        result = [v for k, v in m_fu.sorted_by_generated_order({
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'z': 7,
        })]
        self.assertEqual(result[:5], [1, 7, 3, 2, 4])

    def test_sorted_by_generated_order_with_prioritized_keys(self):
        self.ModelFixtureUpper.generated_field_order = ['a', 'z', 'c', 'b']
        m_fu = self.ModelFixtureUpper()
        result = [v for k, v in m_fu.sorted_by_generated_order({
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'z': 7,
            'g': 8,
            'h': 9,
        }, other_prioritized={'g', 'f'})]

        self.assertEqual(result[:4], [1, 7, 3, 2])
        self.assertEqual(set(result[4:6]), {8, 6})

    def test_sorted_by_generator_order(self):
        self.ModelFixtureUpper.all_fixtures_order = ['a', 'b', 'TestModelFixture', 'c']

        class TestModelFixture(object):
            pass

        class TestNotInOrderModelFixture(object):
            pass

        a = TestModelFixture()
        b = TestNotInOrderModelFixture()
        self.assertEqual(self.ModelFixtureUpper.sorted_fixtures_key(a), '0002_TestModelFixture')
        self.assertEqual(self.ModelFixtureUpper.sorted_fixtures_key(b), '0004_TestNotInOrderModelFixture')
