import os
import basic_example
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
        os.unlink(basic_example.app.config['DATABASE'])

    def test_post(self):
        rv = self.app.get('/')
        assert b'No entries here so far' in rv.data


if __name__ == '__main__':
    unittest.main()
