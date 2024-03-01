from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.utils import iteritems

from mock import Mock
from unittest import TestCase

from fixtureupper.register import UpperRegister


class BaseTestModelFixtureUpper(TestCase):
    def setUp(self):
        class ModelFixtureUpper(UpperRegister('Model')):
            model = Mock()

            def get_model_attr_key(self, *args, **kwargs):
                return 'attr_key'

            def set_relation(self, fixture, related_fixtures, relation_prop):
                setattr(fixture, relation_prop, 'related value: %s' % related_fixtures)

            @classmethod
            def get_relationships(cls):
                return {'rel_1': Mock(), 'rel_2': Mock(), 'rel_3': Mock()}

        self.ModelFixtureUpper = ModelFixtureUpper


class TestModelFixtureUpper(BaseTestModelFixtureUpper):
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

    def test_set_fixture_values(self):
        fixture = Mock(rel_1=None, rel_2=None, static_2=None, static_3=None, static_4='val')
        m_fu = self.ModelFixtureUpper()
        fixture2 = m_fu.set_fixture_values({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        }, fixture=fixture)

        self.assertEqual(fixture, fixture2)
        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_2, None)
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertEqual(fixture.static_2, None)
        self.assertEqual(fixture.static_3, 4)
        self.assertEqual(fixture.static_4, 'val')

    def test_set_fixture_values_creates_fixture_if_None(self):
        m_fu = self.ModelFixtureUpper()
        fixture = m_fu.set_fixture_values({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        })

        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertEqual(fixture.static_3, 4)


class TestModelFixtureUpperFixup(BaseTestModelFixtureUpper):
    def setUp(self):
        super(TestModelFixtureUpperFixup, self).setUp()
        self.ModelFixtureUpper.defaults = {
            'static_2': 30,
            'static_4': 50,
        }

    def test_single_fixup(self):
        m_fu = self.ModelFixtureUpper()
        fixture = m_fu.single_fixup({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        })

        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertEqual(fixture.static_2, 30)
        self.assertEqual(fixture.static_3, 4)
        self.assertEqual(fixture.static_4, 50)
        self.assertEqual(m_fu.fixtures[0], fixture)

    def test_single_fixup_new_default(self):
        m_fu = self.ModelFixtureUpper()
        fixture = m_fu.single_fixup({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        }, defaults={
            'static_4': 70,
            'static_5': 80,
        })

        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertIsInstance(fixture.static_2, Mock)
        self.assertEqual(fixture.static_3, 4)
        self.assertEqual(fixture.static_4, 70)
        self.assertEqual(fixture.static_5, 80)

    def test_single_fixup_default_overrides(self):
        m_fu = self.ModelFixtureUpper()
        fixture = m_fu.single_fixup({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        }, default_overrides={
            'static_4': 90,
        })

        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertEqual(fixture.static_2, 30)
        self.assertEqual(fixture.static_3, 4)
        self.assertEqual(fixture.static_4, 90)
        self.assertIsInstance(fixture.static_5, Mock)

    def test_single_fixup_new_default_and_default_overrides(self):
        m_fu = self.ModelFixtureUpper()
        fixture = m_fu.single_fixup({
            'rel_1': lambda *args: 5,
            'rel_3': 10,
            'static_1': 20,
            'static_3': lambda *args: 4,
        }, defaults={
            'static_4': 70,
            'static_5': 80,
        }, default_overrides={
            'static_4': 90,
        })

        self.assertEqual(fixture.rel_1, 'related value: 5')
        self.assertEqual(fixture.rel_3, 'related value: 10')
        self.assertEqual(fixture.static_1, 20)
        self.assertIsInstance(fixture.static_2, Mock)
        self.assertEqual(fixture.static_3, 4)
        self.assertEqual(fixture.static_4, 90)
        self.assertEqual(fixture.static_5, 80)
