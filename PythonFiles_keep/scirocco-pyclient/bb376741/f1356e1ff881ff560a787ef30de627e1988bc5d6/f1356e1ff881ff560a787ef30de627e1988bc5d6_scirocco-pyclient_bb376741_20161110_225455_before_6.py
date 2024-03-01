import unittest

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.systemdata import SystemData, SystemDataHTTPHeadersDescriptor
from test.mocks import RequestAdapterMock


class MessageQueueDAOTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        system_data_descriptor = SystemDataHTTPHeadersDescriptor(SystemData())

        self.dao = MessageQueueDAO(self.request_adapter, system_data_descriptor)

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, "extraparam")
        res = self.dao.pull()
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['method'], 'GET')

    def test_push(self):
        self.request_adapter.response_status = 201
        self.assertTrue("push" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.push, "destination", "data", "extraparam", "ssdsd")
        msg = {"data": "test"}

        res = self.dao.push('af123', msg.copy(), '.extension')
        self.assertTrue(isinstance(res.message_data, dict))
        self.assertDictEqual(res.message_data, msg)
        self.assertEquals(res.system_data['method'], 'POST')
        self.assertEquals(res.system_data['url'], '/messageQueue')
        self.assertEquals(res.system_data['Scirocco-To'], 'af123')

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEquals(res.system_data['method'], 'PATCH')
        self.assertEquals(res.system_data['url'], '/messageQueue/af123/ack')

    def test_pull_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.pull)

    def test_push_response_different_from_201_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.push, "af123", "message", ".extension")

    def test_ack_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.ack, "af123")
