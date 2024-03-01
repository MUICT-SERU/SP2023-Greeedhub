import unittest

from . import basic_colander_example


class BasicColanderTestCase(unittest.TestCase):
    def setUp(self):
        basic_colander_example.app.config['DATABASE'] = 'sqlite:///:memory:'
        basic_colander_example.app.config['TESTING'] = True
        self.app = basic_colander_example.app.test_client()
        # with basic_colander_example.app.app_context():
        #     basic_colander_example.init_db()

    def tearDown(self):
        # basic_declarative_example.close_db()
        pass

    def test_post(self):
        with basic_colander_example.app.app_context():
            rv = self.app.post('/post', content_type='application/json',
                               data='{"post_value": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.", "author": {"author_name": "John Doe"}}')
            rv = self.app.get('/post/' + str(rv.data, 'utf-8'))
            assert b'{\n  "author_id": "1", \n  "post_id": "1", \n  "post_value": "Lorem ipsum dolor sit amet, consectetur adipiscing elit."\n}' \
                   in rv.data and rv.status_code == 200

    def test_author(self):
        with basic_colander_example.app.app_context():
            rv = self.app.post('/author', content_type='application/json',
                               data='{"author_name": "John Doe", "posts": [{"post_value": "Lorem ipsum dolor sit amet, consectetur adipiscing elit." },'
                                    ' {"post_value": "Test Post"}]}')
            rv = self.app.get('/author/' + str(rv.data, 'utf-8'))
            assert b'{\n  "author_id": "1", \n  "author_name": "John Doe"\n}' in rv.data and rv.status_code == 200


if __name__ == '__main__':
    unittest.main()
