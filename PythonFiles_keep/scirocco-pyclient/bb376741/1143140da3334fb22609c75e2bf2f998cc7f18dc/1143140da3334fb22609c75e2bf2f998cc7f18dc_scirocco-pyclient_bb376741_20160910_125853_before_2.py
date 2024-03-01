import unittest

from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.http.requestadapter import RequestManagerResponseHandler
from sciroccoclient.http.requestadapter import RequestsAdapter
from test.mocks import RequestManagerMock


class MessageQueueDAOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_adapter = RequestsAdapter('https://dds.sandboxwebs.com', 'af123', 'tok', RequestManagerMock(),
                                               RequestManagerResponseHandler())
        cls.dao = MessageQueueDAO(cls.request_adapter)

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, 34, "extraparam")
        res = self.dao.pull()
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['method'], 'GET')

    def test_pull_quantity(self):
        qty = 23
        res = self.dao.pull(qty)
        self.assertTrue('quantity' in res.message_data)
        self.assertEquals(res.message_data['quantity'], qty)
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['method'], 'GET')

    def test_push(self):
        self.assertTrue("push" in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "extraparam")
        self.request_adapter.expected_http_status = 201

        msg = {
            "to_node_id": "af12345",
            "data": {"data": "test"}
        }

        res = self.dao.push(msg.copy())
        self.assertTrue(isinstance(res.message_data, dict))
        self.assertDictEqual(res.message_data, msg['data'])
        self.assertEquals(res.system_data['method'], 'POST')
        self.assertEquals(res.system_data['url'], '/messageQueue')

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEquals(res.http_headers['method'], 'PATCH')
        self.assertEquals(res.http_headers['url'], '/messageQueue/af123/ack')
