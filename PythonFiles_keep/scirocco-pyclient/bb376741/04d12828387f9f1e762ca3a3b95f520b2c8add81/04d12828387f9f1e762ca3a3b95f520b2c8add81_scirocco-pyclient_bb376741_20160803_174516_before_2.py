import unittest

from client.dao.messagequeuedao import MessageQueueDAO
from test.mocks import RequestAdapterMock


class MessageQueueDAOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_adapter = RequestAdapterMock()
        cls.dao = MessageQueueDAO(cls.request_adapter)

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, 34, "extraparam")
        res = self.dao.pull()
        self.assertEquals(res['url'], '/messageQueue')
        self.assertEquals(res['method'], 'GET')

    def test_pull_quantity(self):
        qty = 23
        res = self.dao.pull(qty)
        self.assertTrue('quantity' in res['fields'])
        self.assertEquals(res['fields']['quantity'], qty)
        self.assertEquals(res['url'], '/messageQueue')
        self.assertEquals(res['method'], 'GET')

    def test_push(self):
        self.assertTrue("push" in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "extraparam")

        msg = {
            "to_node_id": "af12345",
            "data": {"data": "test"}
        }

        res = self.dao.push(msg)
        self.assertTrue(isinstance(res['fields'], dict))
        self.assertDictEqual(res['fields'], msg)
        self.assertEquals(res['method'], 'POST')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['url'], '/messageQueue')

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEquals(res['method'], 'PATCH')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['url'], '/messageQueue/af123/ack')
