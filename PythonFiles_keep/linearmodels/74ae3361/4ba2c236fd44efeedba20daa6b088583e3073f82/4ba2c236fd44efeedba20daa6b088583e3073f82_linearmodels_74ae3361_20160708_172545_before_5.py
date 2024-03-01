from unittest import TestCase, skip

import numpy as np
import scipy.sparse as sparse
from nose.tools import assert_is_instance, assert_raises, assert_true
from numpy.testing import assert_equal

from panel.fixed_effects import DummyVariableIterator


class TestDummyIterator(TestCase):
    @classmethod
    def setUpClass(cls):
        np.random.seed(1234)
        cls.n1, cls.t1 = 1000,100
        cls.n2, cls.t2 = 250, 40
        cls.n3, cls.t3 = 5000, 200
        cls.groups1 = np.random.randint(0, 2, size=(cls.n1*cls.t1,))
        cls.groups2 = np.random.randint(0, 100, size=(cls.n2*cls.t2,))
        cls.groups3 = np.random.randint(0, 1000, size=(cls.n3*cls.t3,))

    @skip('Skip very large for now')
    def test_very_large(self):
        size = len(self.groups3)
        n = 20000
        t = size // n
        dvi = DummyVariableIterator(n, t, self.groups3)
        for du in dvi:
            assert_equal(du.shape[1], 1)

        total = np.zeros(size)
        dvi = DummyVariableIterator(n, t, self.groups3, max_size=100)
        for du in dvi:
            assert_equal(du.shape[0], size)
            total += du.sum(1)
        assert_equal(total, np.ones(size))

    def test_equivalence(self):
        d1 = DummyVariableIterator(200, 50, self.groups2, max_size=100)
        for d in d1:
            dummies = d
        assert_equal(dummies.shape[0], self.groups2.shape[0])
        assert_equal(dummies.shape[1], self.groups2.max() + 1)

        d2 = DummyVariableIterator(200, 50, self.groups2, max_size=1)
        blocked = []
        for d in d2:
            blocked.append(d)
        blocked = np.column_stack(blocked)
        assert_equal(blocked.shape[0], self.groups2.shape[0])
        assert_equal(blocked.shape[1], self.groups2.max() + 1)

        assert_equal(dummies, blocked)

    def test_sparse(self):
        n = 20000
        t = len(self.groups3) // n
        dvi = DummyVariableIterator(n, t, self.groups3, sparse=True, max_size=100)
        for du in dvi:
            pass
        assert_is_instance(du, sparse.csc.csc_matrix)

    def test_errors(self):
        group = np.random.randint(0, 200, 10000)
        assert_raises(ValueError, DummyVariableIterator, 200, 50, 2 * group)
        assert_raises(ValueError, DummyVariableIterator, 200, 50, group + 1)
        assert_raises(ValueError, DummyVariableIterator, 200, 50, group[:100])

    def test_drop(self):
        dvi = DummyVariableIterator(self.n1, self.t1, self.groups1)
        dvi_drop = DummyVariableIterator(self.n1, self.t1, self.groups1, drop=True)
        for d, d_dropped in zip(dvi, dvi_drop):
            assert_equal(d.shape[1], d_dropped.shape[1] + 1)

        dvi = DummyVariableIterator(self.n2, self.t2, self.groups2)
        dvi_drop = DummyVariableIterator(self.n2, self.t2, self.groups2, drop=True)
        for d, d_dropped in zip(dvi, dvi_drop):
            assert_equal(d.shape[1], d_dropped.shape[1] + 1)

        dvi = DummyVariableIterator(self.n3, self.t3, self.groups3)
        dvi_drop = DummyVariableIterator(self.n3, self.t3, self.groups3, drop=True)
        count = 0
        for d, d_dropped in zip(dvi, dvi_drop):
            assert_true(np.all(d*d_dropped == 0))
            count += 1
            if count > 2:
                break
