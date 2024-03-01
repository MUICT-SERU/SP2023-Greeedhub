# coding=utf-8

import unittest

from lxml_asserts.compat import unicode_type
from lxml_asserts.testcase import LxmlTestCaseMixin

from .common import CommonBase


class TestXmlEqual(unittest.TestCase, LxmlTestCaseMixin, CommonBase):
    assert_function = LxmlTestCaseMixin.assertXmlEqual
    format_message = u'XML documents are not equal — {}'.format

    def test_assertXmlEqual_different_children_order_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlEqual('<a><b><c/><d/></b></a>', '<a><b><d/><c/></b></a>', check_tags_order=True)

        self.assertEqual(
            unicode_type(e.exception), u'XML documents are not equal — Tags do not match: /a/b/c != /a/b/d'
        )

    def test_assertXmlEqual_added_attribute_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlEqual('<a y="2"/>', '<a x="1" y="2"/>')

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u'Second xml has additional attributes: /a/(x)')
        )

    def test_assertXmlEqual_different_children_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlEqual('<a><b/><c/></a>', '<a><d/><b/></a>')

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u'No equal child found in second xml: /a/c')
        )

    def test_assertXmlEqual_different_child_tail_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlEqual('<a><b/>123</a>', '<a><b/>абв</a>')

        self.assertEqual(
            unicode_type(e.exception), self.format_message(u'No equal child found in second xml: /a/b')
        )

    def test_assertXmlEqual_missing_child_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlEqual('<a><b/><c/></a>', '<a><b/></a>')

        self.assertEqual(
            unicode_type(e.exception), self.format_message(u'Children are not equal: /a[2 children != 1 children]')
        )
