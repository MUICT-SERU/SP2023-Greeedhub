from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.utils import iteritems

from mock import Mock
from unittest import TestCase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import backref, relation


from fixtureupper.register import UpperRegister


@as_declarative()
class _Base(object):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


class A(_Base):
    b_id = Column(Integer, ForeignKey('b.id'))
    b = relation('B', backref='a')

    c_id = Column(Integer, ForeignKey('c.id'))
    c = relation('C', backref=backref('a', uselist=False))

    d_id = Column(Integer, ForeignKey('d.id'))
    d = relation('D', back_populates='a')

    e = relation('E', backref='a')


class B(_Base):
    pass


class C(_Base):
    pass


class D(_Base):
    a = relation('A', back_populates='d')


class E(_Base):
    a_id = Column(Integer, ForeignKey('a.id'))


class BaseTestMockFixtureUpper(TestCase):
    def setUp(self):
        class MockFixtureUpper(UpperRegister('SqlAlchemyModel')):
            model = A

        self.MockFixtureUpper = MockFixtureUpper


class TestSetRelations(BaseTestMockFixtureUpper):
    def test_a_b(self):
        a = A(id=1)
        b = B(id=2)
        self.MockFixtureUpper().set_relation(a, b, 'b')
        self.assertEqual(a.b_id, 2)

    def test_b_a(self):
        a = [A(id=1), A(id=2)]
        b = B(id=3)
        self.MockFixtureUpper().set_relation(b, a, 'a')
        self.assertEqual(a[0].b_id, 3)
        self.assertEqual(a[1].b_id, 3)

    def test_a_c(self):
        a = A(id=1)
        c = C(id=2)
        self.MockFixtureUpper().set_relation(a, c, 'c')
        self.assertEqual(a.c_id, 2)

    def test_c_a(self):
        a = A(id=1)
        c = C(id=2)
        self.MockFixtureUpper().set_relation(c, a, 'a')
        self.assertEqual(a.c_id, 2)

    def test_a_d(self):
        a = A(id=1)
        d = D(id=2)
        self.MockFixtureUpper().set_relation(a, d, 'd')
        self.assertEqual(a.d_id, 2)

    def test_d_a(self):
        a = [A(id=1), A(id=2)]
        d = D(id=3)
        self.MockFixtureUpper().set_relation(d, a, 'a')
        self.assertEqual(a[0].d_id, 3)
        self.assertEqual(a[1].d_id, 3)

    def test_a_e(self):
        a = A(id=1)
        e = [E(id=2), E(id=3)]
        self.MockFixtureUpper().set_relation(a, e, 'e')
        self.assertEqual(e[0].a_id, 1)
        self.assertEqual(e[1].a_id, 1)

    def test_a_e(self):
        a = A(id=1)
        e = E(id=2)
        self.MockFixtureUpper().set_relation(e, a, 'a')
        self.assertEqual(e.a_id, 1)

    def test_a_e_with_no_id(self):
        a = A()
        e = E()
        self.MockFixtureUpper().set_relation(e, a, 'a')
        self.assertEqual(e.a_id, None)
