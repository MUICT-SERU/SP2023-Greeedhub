# coding=utf-8

import unittest

from lxml_asserts.compat import unicode_type
from lxml_asserts.testcase import LxmlTestCaseMixin

from .common import CommonBase


class TestXmlCompatible(unittest.TestCase, LxmlTestCaseMixin, CommonBase):
    assert_function = LxmlTestCaseMixin.assertXmlCompatible
    format_message = u'XML documents are not compatible — {}'.format

    def test_assertXmlCompatible_added_attributes(self):
        tree1 = '''
            <elem>
                <a answer="42" douglas="adams"/>
            </elem>
            '''.strip()

        tree2 = '''
            <elem prop="some">
                <a answer="42" new2="no" douglas="adams" new="yes"/>
            </elem>
            '''.strip()

        self.assertXmlCompatible(tree1, tree2)

    def test_assertXmlCompatible_extra_tags(self):
        tree1 = '''
            <elem>
                <z prop="1"/>
                <a>
                    <c/>
                    <c month="jan"/>
                    <b/>
                </a>
                <z prop="3"/>
                <a disabled="true"/>
                <txt>some text</txt>
            </elem>
            '''.strip()

        tree2 = '''
            <elem>
                <a disabled="true"/>
                <a>
                    <aa/>
                    <b/>
                    <c month="apr"/>
                    <c month="jan"/>
                    <c/>
                    <dd/>
                </a>
                <txt>some text</txt>
                <txt>some new text</txt>
                <z prop="3"/>
                <z prop="1">
                    <new nested="tag"/>
                </z>
                <yy/>
            </elem>
            '''.strip()

        self.assertXmlCompatible(tree1, tree2)

    def test_assertXmlCompatible_different_child_tail_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlCompatible('<a><b/>123</a>', '<a><b/>абв</a>')

        self.assertEqual(
            unicode_type(e.exception), self.format_message(u'Second xml has no compatible child for /a/b')
        )

    def test_assertXmlCompatible_missing_child_fail(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlCompatible('<a><b/><c/></a>', '<a><b/></a>')

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u'Second xml /a contains less children (1 < 2)')
        )

    def test_assertXmlCompatible_missing_child_recursive(self):
        with self.assertRaises(AssertionError) as e:
            self.assertXmlCompatible('<a><b><c/><d/></b></a>', '<a><b><c/></b></a>')

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u'Second xml has no compatible child for /a/b')
        )

    def test_assertXmlCompatible_incompatible_attributes(self):
        tree1 = '''
            <elem>
                <a answer="42" douglas="adams"/>
            </elem>
            '''.strip()

        tree2 = '''
            <elem>
                <a douglas="adams" extra="extra"/>
            </elem>
            '''.strip()

        with self.assertRaises(AssertionError) as e:
            self.assertXmlCompatible(tree1, tree2)

        self.assertEqual(
            unicode_type(e.exception),
            self.format_message(u'Second xml has no compatible child for /elem/a')
        )

    def test_assertXmlCompatible_not_enough_compatible(self):
        tree1 = '''
           <root>
               <a x="1"/>
               <a y="1"/>
               <a z="1"><b/></a>
           </root>
        '''

        tree2 = '''
           <root>
               <a x="1" z="1"><b/></a>
               <a y="1"/>
               <a z="1"><c/></a>
           </root>
        '''

        with self.assertRaises(AssertionError) as e:
            self.assertXmlCompatible(tree1, tree2)

        self.assertIn(
            self.format_message(u'Second xml has no compatible child for /root/a'),
            unicode_type(e.exception)
        )
