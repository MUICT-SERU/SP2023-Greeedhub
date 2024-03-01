import unittest

from client.dao.batchqueuedao import BatchQueueDAO
from test.mocks import RequestAdapterMock


class BatchQueueDAOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dao = BatchQueueDAO(RequestAdapterMock())

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/batchQueue')

    def test_get(self):
        self.assertTrue('get' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.get, 'extraparam')

        res = self.dao.get()

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

    def test_update(self):
        self.assertTrue('update' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.update, 'batch_id', 'data', 'extraparam')

        batch_id = 'af123'
        batch_update = {
            "to_node_id": "af12456778",
            "data": [{"data2": "data2"}]
        }
        res = self.dao.update(batch_id, batch_update)

        self.assertEquals(res['method'], 'PATCH')
        self.assertEquals(res['url'], '/batchQueue/af123')
        self.assertEquals(res['headers'], None)
        self.assertDictEqual(res['fields'], batch_update)
