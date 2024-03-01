# Python
#
# This module implements tests for TextUtils class.
#
# This file is part of mdutils. https://github.com/didix21/mdutils
#
# MIT License: (C) 2018 Dídac Coll

from unittest import TestCase
from mdutils.tools.tools import TextUtils

__author__ = 'didix21'
__project__ = 'MdUtils'


class TestTextUtils(TestCase):
    def test_bold(self):
        expects = '**Bold Example**'
        self.assertEqual(TextUtils().bold('Bold Example'), expects)

    def test_italics(self):
        expects = '_Italics Example_'
        self.assertEqual(TextUtils().italics('Italics Example'), expects)

    def test_inline_code(self):
        expects = '`Inline Code Example`'
        self.assertEqual(TextUtils().inline_code('Inline Code Example'), expects)

    def test_center_text(self):
        expects = '<center>Text Center Alignment Example</center>'
        self.assertEqual(TextUtils().center_text('Text Center Alignment Example'), expects)

    def test_text_color(self):
        expects = '<font color="red"> Red Color Example </font>'
        self.assertEqual(TextUtils().text_color('Red Color Example', 'red'), expects)

    def test_text_external_link(self):
        text = 'Text Example'
        link = 'https://link.example.org'
        expects = '[' + text + '](' + link + ')'
        self.assertEqual(TextUtils().text_external_link(text, link), expects)

    def test_text_format(self):
        color = 'red'
        text = 'Text Format'
        text_color = TextUtils().text_color(text, color)
        text_color_center = TextUtils().center_text(text_color)
        text_color_center_b = TextUtils().bold(text_color_center)
        text_color_center_bc = TextUtils().inline_code(text_color_center_b)
        text_color_center_bci = TextUtils().italics(text_color_center_bc)

        expects = text_color_center_bci
        obtains = TextUtils().text_format(text, bold_italics_code='bci', color='red', align='center')

        self.assertEqual(obtains, expects)

