import pytest

from fuzzyfloat import rel_fp


def expect_fp(value, expected):
    assert type(value) == rel_fp
    assert value == expected


def test_cmp_eq():
    value = rel_fp(100.5)

    assert value == 100.5
    assert value == 100.5000001
    assert value == 100.4999999


def test_cmp_le():
    value = rel_fp(100)
    assert value <= 500
    assert value <= 100
    assert value <= 99.9999999
    assert not value <= 50


def test_cmp_ge():
    value = rel_fp(100)
    assert value >= 50
    assert value >= 100
    assert value >= 99.9999999
    assert not value >= 500


def test_add():
    value = rel_fp(100)
    expect_fp(value + value, 200)
    expect_fp(value + 100, 200)
    expect_fp(100 + value, 200)

    value += 100
    expect_fp(value, 200)


def test_sub():
    value = rel_fp(100)
    expect_fp(value - value, 0)
    expect_fp(value - 100, 0)
    expect_fp(100 - value, 0)

    value -= value
    expect_fp(value, 0)
    value -= 100
    expect_fp(value, -100)


def test_mul():
    value = rel_fp(100)
    expect_fp(value * value, 100 * 100)
    expect_fp(value * 100, 100 * 100)
    expect_fp(100 * value, 100 * 100)

    value *= 100
    expect_fp(value, 100 * 100)


def test_div():
    value = rel_fp(100)
    expect_fp(value / value, 1.0)
    expect_fp(value / 100, 1.0)
    expect_fp(100 / value, 1.0)

    value /= value
    expect_fp(value, 1.0)


def test_floordiv():
    value = rel_fp(111)
    expect_fp(value // value, 1)
    expect_fp(value // 10, 11)
    expect_fp(11 // value, 0)

    value //= 10
    expect_fp(value, 11)


def test_exp():
    value = rel_fp(3)
    expect_fp(value ** value, 3 ** 3)
    expect_fp(value ** 3, 3 ** 3)
    expect_fp(3 ** value, 3 ** 3)


def test_divmod():
    pass


def test_mod():
    pass


def test_abs():
    value = rel_fp(-100)
    expect_fp(abs(value), 100)


def test_neg():
    value = rel_fp(100)
    expect_fp(-value, -100)
