# coding=utf-8

import unittest

from lxml import etree

from lxml_asserts.compat import unicode_type


class CommonBase(object):
    assert_function = None
    format_message = None

    assertRaises = unittest.TestCase.assertRaises
    assertEqual = unittest.TestCase.assertEqual

    TREE = '''
        <root attribute1="value1" attribute2="value2">
            <element1/>
            <element2>
                <leaf1/>
                <leaf2 a="1" b="2"/>
            </element2>
        </root>
        '''.strip()

    def test_same_tree(self):
        tree = etree.fromstring(self.TREE)
        self.assert_function(tree, tree)

    def test_different_attributes_order(self):
        self.assert_function('<a x="1" y="2"/>', '<a y="2" x="1"/>')

    def test_different_children_order(self):
        another_tree = '''
            <root attribute1="value1" attribute2="value2">
                <element2>
                    <leaf2 a="1" b="2"/>
                    <leaf1/>
                </element2>
                <element1/>
            </root>
            '''.strip()

        self.assert_function(self.TREE, another_tree)

    def test_different_root_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assert_function('<a/>', '<b/>')

        self.assertEqual(unicode_type(e.exception), self.format_message(u'Tags do not match: /a != /b'))

    def test_fail_with_custom_message(self):
        with self.assertRaises(AssertionError) as e:
            self.assert_function('<a/>', '<b/>', msg='Custom message')

        self.assertEqual(unicode_type(e.exception), u'Custom message — Tags do not match: /a != /b')

    def test_missing_attribute_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assert_function('<a x="1" y="2"/>', '<a y="2"/>')

        self.assertEqual(
            unicode_type(e.exception), self.format_message(u'Second xml misses attributes: /a/(x)')
        )

    def test_different_attribute_values_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assert_function('<a x="1" y="2"/>', '<a x="ταБЬℓσ" y="2"/>')

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u"Attribute values are not equal: /a/x['1' != 'ταБЬℓσ']")
        )

    def test_different_tag_text_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assert_function('<a>123</a>', '<a>ταБЬℓσ</a>')

        self.assertEqual(
            unicode_type(e.exception), self.format_message(u"Tags text differs: /a['123' != 'ταБЬℓσ']")
        )

    def test_comments(self):
        self.assert_function(
            b'<?xml version="1.0" encoding="utf-8"?><root><!--a--><c/><!--b--><!--\xd0\xb0\xd0\xb1\xd0\xb2--></root>',
            b'<?xml version="1.0" encoding="utf-8"?><root><!--\xd0\xb0\xd0\xb1\xd0\xb2--><!--b--><c/><!--a--></root>'
        )
