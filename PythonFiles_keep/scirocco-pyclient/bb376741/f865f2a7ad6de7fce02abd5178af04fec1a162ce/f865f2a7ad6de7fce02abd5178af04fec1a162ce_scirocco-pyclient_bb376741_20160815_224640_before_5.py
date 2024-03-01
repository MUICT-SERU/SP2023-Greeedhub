import unittest

from pyddsclient.httpdao.batchqueuedao import BatchQueueDAO
from test.mocks import RequestAdapterMock


class BatchQueueDAOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dao = BatchQueueDAO(RequestAdapterMock())

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/batchQueue')

    def test_pull(self):
        self.assertTrue('pull' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, 'extraparam')

        res = self.dao.pull()

        self.assertEquals(res['method'], 'GET')
        self.assertEquals(res['url'], '/batchQueue')
        self.assertEquals(res['data'], None)
        self.assertEquals(res['headers'], None)

    def test_push(self):
        self.assertTrue('push' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.push, 'batch', 'extraparam')

        batch = {
            "to_node_id": "af123",
            "data": [{"data2": "data2"}]
        }

        res = self.dao.push(batch)

        self.assertEquals(res['method'], 'POST')
        self.assertEquals(res['url'], '/batchQueue')
        self.assertEquals(res['headers'], None)
        self.assertDictEqual(res['data'], batch)

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.ack, 'batch_id', 'data', 'extraparam')

        batch_id = 'af123'

        res = self.dao.ack(batch_id)

        self.assertEquals(res.system_data['method'], 'PATCH')
        self.assertEquals(res.system_data['url'], '/batchQueue/af123/ack')
        self.assertEquals(res.http_headers, None)
        self.assertEquals(res.message_data, None)
