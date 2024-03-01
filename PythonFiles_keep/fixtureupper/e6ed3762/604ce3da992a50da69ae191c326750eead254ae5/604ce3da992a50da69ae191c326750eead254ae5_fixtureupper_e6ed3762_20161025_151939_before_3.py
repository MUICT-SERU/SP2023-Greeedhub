from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from unittest import TestCase

from fixtureupper.core import UpperRegister
from tests.unit.models import Article, Author


class TestUpperRegister(TestCase):
    def setUp(self):
        self.ModelFixtureUpper1 = UpperRegister()
        self.ModelFixtureUpper2 = UpperRegister()

        class AuthorFixtureUpper(self.ModelFixtureUpper1):
            model = Author

        class ArticleFixtureUpper(self.ModelFixtureUpper2):
            model = Article

        self.m_fu_1 = self.ModelFixtureUpper1()
        self.m_fu_2 = self.ModelFixtureUpper2()
        self.AuthorFixtureUpperClass = AuthorFixtureUpper
        self.ArticleFixtureUpperClass = ArticleFixtureUpper

    def test_registers_have_different_generator_classes(self):
        self.assertEqual(type(self.m_fu_1.get_upper('Author')), self.AuthorFixtureUpperClass)
        with self.assertRaises(KeyError):
            self.assertEqual(type(self.m_fu_1.get_upper('Article')), self.ArticleFixtureUpperClass)

        with self.assertRaises(KeyError):
            self.assertEqual(type(self.m_fu_2.get_upper('Author')), self.AuthorFixtureUpperClass)
        self.assertEqual(type(self.m_fu_2.get_upper('Article')), self.ArticleFixtureUpperClass)
