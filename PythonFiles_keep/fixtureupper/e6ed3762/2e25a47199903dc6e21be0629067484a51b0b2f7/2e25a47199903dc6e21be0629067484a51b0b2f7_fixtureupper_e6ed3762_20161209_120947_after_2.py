from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from unittest import TestCase

from fixtureupper.register import UpperRegister
from tests.models import Article, Author, CoWrite, Draft


class BaseTestCase(TestCase):
    def setUp(self):
        self.SqlAlchemyModelFixtureUpper = UpperRegister('SqlAlchemyModel')

        class AuthorFixtureUpper(self.SqlAlchemyModelFixtureUpper):
            model = Author
            defaults = {}

        class ArticleFixtureUpper(self.SqlAlchemyModelFixtureUpper):
            model = Article
            defaults = {}

        class DraftFixtureUpper(self.SqlAlchemyModelFixtureUpper):
            model = Draft
            defaults = {}

        class CoWriteFixtureUpper(self.SqlAlchemyModelFixtureUpper):
            model = CoWrite
            defaults = {}

        self.m_fu = self.SqlAlchemyModelFixtureUpper(start_id=150)
        self.AuthorFixtureUpperClass = AuthorFixtureUpper
        self.ArticleFixtureUpperClass = ArticleFixtureUpper
        self.DraftFixtureUpperClass = DraftFixtureUpper
        self.CoWriteFixtureUpperClass = CoWriteFixtureUpper

        self.au_fu = self.m_fu.get_upper('Author')
        self.ar_fu = self.m_fu.get_upper('Article', start_id=250)
        self.dr_fu = self.m_fu.get_upper('Draft', start_id=300)
        self.co_fu = self.m_fu.get_upper('CoWrite', start_id=370)

        self.json_dict = [
            {
                '__class__': 'Article',
                '__value__': {'id': 250, 'main_author_id': 150}
            },
            {
                '__class__': 'Article',
                '__value__': {'id': 251, 'main_author_id': 150}
            },
            {
                '__class__': 'Article',
                '__value__': {
                    'id': 252,
                    'main_author_id': 151,
                    'is_visible': True,
                    'title': u'some title',
                }
            },
            {
                '__class__': 'Author',
                '__value__': {'id': 150}
            },
            {
                '__class__': 'Author',
                '__value__': {'id': 151}
            },
        ]
