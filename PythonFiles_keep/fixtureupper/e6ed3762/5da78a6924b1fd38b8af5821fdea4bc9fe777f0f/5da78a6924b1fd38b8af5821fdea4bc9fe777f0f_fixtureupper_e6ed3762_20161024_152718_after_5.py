from unittest import TestCase

from fixtureupper import UpperRegister
from models import Article, Author


class TestModelFixtureUpper(TestCase):
    def setUp(self):
        self.ModelFixtureUpper = UpperRegister()

        class AuthorFixtureUpper(self.ModelFixtureUpper):
            model = Author

        class ArticleFixtureUpper(self.ModelFixtureUpper):
            model = Article

        self.AuthorFixtureUpper = AuthorFixtureUpper
        self.ArticleFixtureUpper = ArticleFixtureUpper

    def test_register_fixture_uppers(self):
        model_fixture_upper = self.ModelFixtureUpper()
        self.assertEqual(type(model_fixture_upper.get_upper('Author')), self.AuthorFixtureUpper)
        self.assertEqual(type(model_fixture_upper.get_upper('Article')), self.ArticleFixtureUpper)
