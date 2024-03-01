import unittest

from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from test.mocks import RequestAdapterMock


class MessageQueueDAOTest(unittest.TestCase):

    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        self.dao = MessageQueueDAO(self.request_adapter)

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, 34, "extraparam")
        res = self.dao.pull()
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['method'], 'GET')

    def test_push(self):
        self.request_adapter.response_status = 201
        self.assertTrue("push" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.push, "destination", "data", "extraparam")
        msg = {"data": "test"}

        res = self.dao.push('af123', msg.copy())
        print(res.system_data)
        self.assertTrue(isinstance(res.message_data, dict))
        self.assertDictEqual(res.message_data, msg)
        self.assertEquals(res.system_data['method'], 'POST')
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['Scirocco-Id'], 'af123')

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEquals(res.system_data['method'], 'PATCH')
        self.assertEquals(res.system_data['url'], '/messageQueue/af123/ack')
