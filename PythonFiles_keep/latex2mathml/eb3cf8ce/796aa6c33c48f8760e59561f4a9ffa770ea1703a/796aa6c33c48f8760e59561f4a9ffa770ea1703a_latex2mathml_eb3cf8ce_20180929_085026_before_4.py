#!/usr/bin/env python
# __author__ = "Ronie Martinez"
# __copyright__ = "Copyright 2016-2018, Ronie Martinez"
# __credits__ = ["Ronie Martinez"]
# __license__ = "MIT"
# __maintainer__ = "Ronie Martinez"
# __email__ = "ronmarti18@gmail.com"
# __status__ = "Development"
import xml.etree.cElementTree as eTree
from xml.sax.saxutils import unescape

# noinspection PyPackageRequirements
import pytest

from latex2mathml.converter import convert


@pytest.fixture
def math_and_row():
    math = eTree.Element('math')
    row = eTree.SubElement(math, 'mrow')
    yield math, row


def test_subscript(math_and_row):
    math, row = math_and_row
    sub = eTree.SubElement(row, 'msub')
    mi = eTree.SubElement(sub, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(sub, 'mi')
    mi.text = 'b'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('a_b')


def test_superscript(math_and_row):
    math, row = math_and_row
    sup = eTree.SubElement(row, 'msup')
    mi = eTree.SubElement(sup, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(sup, 'mi')
    mi.text = 'b'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('a^b')


def test_subscript_and_superscript(math_and_row):
    math, row = math_and_row
    subsup = eTree.SubElement(row, 'msubsup')
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'b'
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'c'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('a_b^c')


def test_superscript_and_subscript(math_and_row):
    math, row = math_and_row
    subsup = eTree.SubElement(row, 'msubsup')
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'c'
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'b'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('a^b_c')


def test_subscript_within_curly_braces(math_and_row):
    math, row = math_and_row
    row = eTree.SubElement(row, 'mrow')
    sub = eTree.SubElement(row, 'msub')
    mi = eTree.SubElement(sub, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(sub, 'mi')
    mi.text = 'b'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('{a_b}')


def test_superscript_within_curly_braces(math_and_row):
    math, row = math_and_row
    row = eTree.SubElement(row, 'mrow')
    sup = eTree.SubElement(row, 'msup')
    mi = eTree.SubElement(sup, 'mi')
    mi.text = 'a'
    mi = eTree.SubElement(sup, 'mi')
    mi.text = 'b'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('{a^b}')


def test_superscript_with_curly_braces(math_and_row):
    math, row = math_and_row
    subsup = eTree.SubElement(row, 'msubsup')
    mi = eTree.SubElement(subsup, 'mi')
    mi.text = 'a'
    mn = eTree.SubElement(subsup, 'mn')
    mn.text = '3'
    row = eTree.SubElement(subsup, 'mrow')
    mi = eTree.SubElement(row, 'mi')
    mi.text = 'i'
    mo = eTree.SubElement(row, 'mo')
    mo.text = '&#x0002B;'
    mn = eTree.SubElement(row, 'mn')
    mn.text = '1'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('a^{i+1}_3')


def test_simple_fraction(math_and_row):
    math, row = math_and_row
    frac = eTree.SubElement(row, 'mfrac')
    row = eTree.SubElement(frac, 'mrow')
    mn = eTree.SubElement(row, 'mn')
    mn.text = '1'
    row = eTree.SubElement(frac, 'mrow')
    mn = eTree.SubElement(row, 'mn')
    mn.text = '2'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\frac{1}{2}')


def test_square_root(math_and_row):
    math, row = math_and_row
    sqrt = eTree.SubElement(row, 'msqrt')
    row = eTree.SubElement(sqrt, 'mrow')
    mn = eTree.SubElement(row, 'mn')
    mn.text = '2'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\sqrt{2}')


def test_root(math_and_row):
    math, row = math_and_row
    root = eTree.SubElement(row, 'mroot')
    row = eTree.SubElement(root, 'mrow')
    mn = eTree.SubElement(row, 'mn')
    mn.text = '2'
    row = eTree.SubElement(root, 'mrow')
    mn = eTree.SubElement(row, 'mn')
    mn.text = '3'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\sqrt[3]{2}')


def test_binomial(math_and_row):
    math, row = math_and_row
    mo = eTree.SubElement(row, 'mo')
    mo.text = '&#x00028;'
    frac = eTree.SubElement(row, 'mfrac', linethickness="0")
    _row = eTree.SubElement(frac, 'mrow')
    mn = eTree.SubElement(_row, 'mn')
    mn.text = '2'
    _row = eTree.SubElement(frac, 'mrow')
    mn = eTree.SubElement(_row, 'mn')
    mn.text = '3'
    mo = eTree.SubElement(row, 'mo')
    mo.text = '&#x00029;'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\binom{2}{3}')


def test_left_and_right(math_and_row):
    math, row = math_and_row
    mo = eTree.SubElement(row, 'mo', stretchy='true', form='prefix', fence='true')
    mo.text = '&#x00028;'
    mi = eTree.SubElement(row, 'mi')
    mi.text = 'x'
    mo = eTree.SubElement(row, 'mo', stretchy='true', form='postfix', fence='true')
    mo.text = '&#x00029;'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\left(x\right)')


def test_space(math_and_row):
    math, row = math_and_row
    eTree.SubElement(row, 'mspace', width='0.167em')
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert('\,')


def test_overline(math_and_row):
    math, row = math_and_row
    over = eTree.SubElement(row, 'mover')
    row = eTree.SubElement(over, 'mrow')
    mi = eTree.SubElement(row, 'mi')
    mi.text = 'a'
    mo = eTree.SubElement(over, 'mo', stretchy='true')
    mo.text = '&#x000AF;'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\overline{a}')


def test_underline(math_and_row):
    math, row = math_and_row
    under = eTree.SubElement(row, 'munder')
    mrow = eTree.SubElement(under, 'mrow')
    mi = eTree.SubElement(mrow, 'mi')
    mi.text = 'a'
    mo = eTree.SubElement(under, 'mo', stretchy='true')
    mo.text = '&#x00332;'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\underline{a}')


def test_matrix(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'a'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'b'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'c'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'd'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{matrix}a & b \\ c & d \end{matrix}')


def test_matrix_without_begin_and_end(math_and_row):  # taken from MathJax
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'a'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'b'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'c'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'd'

    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\matrix{a & b \\ c & d}')


def test_matrix_with_alignment(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'a'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'b'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'c'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'd'

    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{matrix*}[r]a & b \\ c & d \end{matrix*}')


def test_matrix_with_negative_sign(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mo = eTree.SubElement(td, 'mo')
    mo.text = '&#x02212;'
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'a'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'b'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'c'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'd'

    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{matrix}-a & b \\ c & d \end{matrix}')


def test_pmatrix(math_and_row):
    math, row = math_and_row
    mo = eTree.SubElement(row, 'mo')
    mo.text = '&#x00028;'
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'a'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'b'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'c'
    td = eTree.SubElement(tr, 'mtd')
    mi = eTree.SubElement(td, 'mi')
    mi.text = 'd'

    mo = eTree.SubElement(row, 'mo')
    mo.text = '&#x00029;'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{pmatrix}a & b \\ c & d \end{pmatrix}')


def test_simple_array(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable')

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '1'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '2'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '3'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '4'

    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{array}{cr} 1 & 2 \\ 3 & 4 \end{array}''')


def test_array_with_vertical_bars(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable', columnlines='solid none')
    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '1'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '2'
    td = eTree.SubElement(tr, 'mtd', columnalign='left')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '3'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '4'
    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '5'
    td = eTree.SubElement(tr, 'mtd', columnalign='left')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '6'

    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{array}{c|rl} 1 & 2 & 3 \\ 4 & 5 & 6 \end{array}''')


def test_array_with_horizontal_lines(math_and_row):
    math, row = math_and_row
    table = eTree.SubElement(row, 'mtable', rowlines="none solid")

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '1'

    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '2'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '3'

    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '4'

    tr = eTree.SubElement(table, 'mtr')
    td = eTree.SubElement(tr, 'mtd', columnalign='center')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '5'

    td = eTree.SubElement(tr, 'mtd', columnalign='right')
    mn = eTree.SubElement(td, 'mn')
    mn.text = '6'
    xml_string = eTree.tostring(math)
    try:
        expected = unescape(xml_string)
    except TypeError:  # pragma: nocover_py2
        expected = unescape(xml_string.decode('utf-8'))
    assert expected == convert(r'\begin{array}{cr} 1 & 2 \\ 3 & 4 \\ \hline 5 & 6 \end{array}''')
