import pytest

from py_algorithms.sort import new_merge_sort
from tests.conftest import large_xs
from tests.conftest import xs


class TestMergeSort:
    def test_sorting_algorithm(self):
        f = new_merge_sort()
        assert sorted(xs()) == f(xs())

    def test_sorting_algorithm_on_large_xs(self):
        f = new_merge_sort()
        assert sorted(large_xs()) == f(large_xs())

    def test_non_iterable_xs(self):
        f = new_merge_sort()
        for x in (None, 1, ''):
            with pytest.raises(RuntimeError):
                f(x)
