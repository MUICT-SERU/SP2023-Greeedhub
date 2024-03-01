import os
from . import basic_example
import unittest
import tempfile


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        basic_example.app.config['DATABASE'] = 'sqlite:///:memory:'
        basic_example.app.config['TESTING'] = True
        self.app = basic_example.app.test_client()
        with basic_example.app.app_context():
            basic_example.init_db()

    def tearDown(self):
        # basic_declarative_example.close_db()
        pass

    def test_post(self):
        rv = self.app.post('/', data='{"post_value": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "author": {"author_name": "John Doe"}}',
                           content_type='application/json')
        assert b'' in rv.data and rv.status_code == 200


if __name__ == '__main__':
    unittest.main()
