import unittest

from pyddsclient.httpdao.batchdao import BatchDAO
from test.mocks import RequestAdapterMock


class BatchDAOTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_adapter = RequestAdapterMock()
        cls.dao = BatchDAO(cls.request_adapter)

    def test_end_point(self):
        self.assertEquals(self.dao.end_point, '/batches')

    def test_get_all(self):
        self.assertTrue('get_all' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.get_all, "extraparam")

        res = self.dao.get_all()

        self.assertEquals(res['method'], 'GET')
        self.assertEquals(res['url'], '/batches')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['data'], None)

    def test_get_one(self):
        self.assertTrue('get_one' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "af123", "extraparam")

        res = self.dao.get_one("af123")

        self.assertEquals(res['method'], 'GET')
        self.assertEquals(res['url'], '/batches/af123')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['data'], None)

    def test_delete_one(self):
        self.assertTrue('delete_one' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "af123", "extraparam")

        res = self.dao.delete_one("af123")

        self.assertEquals(res['method'], 'DELETE')
        self.assertEquals(res['url'], '/batches/af123')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['data'], None)

    def test_delete_all(self):
        self.assertTrue('delete_all' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "extraparam")

        res = self.dao.delete_all()

        self.assertEquals(res['method'], 'DELETE')
        self.assertEquals(res['url'], '/batches')
        self.assertEquals(res['headers'], None)
        self.assertEquals(res['data'], None)

    def test_update_one(self):
        data_to_update_fixture = {"data": "data"}

        self.assertTrue('update_one' in dir(self.dao))
        self.assertRaises(TypeError, self.dao.update_one, "af123", data_to_update_fixture, "extraparam")

        res = self.dao.update_one("af123", data_to_update_fixture)

        self.assertEquals(res['method'], 'PATCH')
        self.assertEquals(res['url'], '/batches/af123')
        self.assertEquals(res['headers'], None)
        self.assertDictEqual(res['data'], data_to_update_fixture)
