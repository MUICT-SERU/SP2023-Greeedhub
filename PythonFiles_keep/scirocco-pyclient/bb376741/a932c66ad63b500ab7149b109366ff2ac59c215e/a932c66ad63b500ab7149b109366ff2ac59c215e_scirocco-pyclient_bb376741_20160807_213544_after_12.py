import unittest

from client.httpdao.batchqueuedao import BatchQueueDAO
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
        self.assertEquals(res['fields'], None)
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
        self.assertDictEqual(res['fields'], batch)

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.ack, 'batch_id', 'data', 'extraparam')

        batch_id = 'af123'

        res = self.dao.ack(batch_id)

        self.assertEquals(res['method'], 'PATCH')
        self.assertEquals(res['url'], '/batchQueue/af123/ack')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['fields'], None)
