import unittest

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.http.messagedao import MessageDAO
from test.unit.mocks import RequestAdapterMock


class MessageDAOTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        self.dao = MessageDAO(self.request_adapter)

    def test_end_point(self):
        self.assertEquals('/messages', self.dao.end_point)

    def test_get_one(self):
        self.assertTrue("get_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.get_one)
        self.assertRaises(TypeError, self.dao.get_one, "extraparam", "extraparam")
        res = self.dao.get_one("af123")
        self.assertEquals('GET', res.system_data['method'])
        self.assertEquals(self.dao.end_point + '/af123', res.system_data['url'])

    def test_get_all(self):
        self.assertTrue("get_all" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.get_all, "extraparam")

        res = self.dao.get_all()
        self.assertEquals('GET', res.system_data['method'])
        self.assertEquals(self.dao.end_point, res.system_data['url'])

    def test_delete_one(self):
        self.assertTrue("delete_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.delete_one)
        self.assertRaises(TypeError, self.dao.delete_one, "extraparam", "extraparam")

        res = self.dao.delete_one('af123')
        self.assertEquals('DELETE', res.system_data['method'])
        self.assertEquals(self.dao.end_point + '/af123', res.system_data['url'])

    def test_delete_all(self):
        self.assertTrue("delete_all" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.delete_all, "extraparam")

        res = self.dao.delete_all()
        self.assertEquals('DELETE', res.system_data['method'])
        self.assertEquals(self.dao.end_point, res.system_data['url'])

    def test_update_one(self):
        self.assertTrue("update_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.update_one)
        self.assertRaises(TypeError, self.dao.update_one, "correct_param", "correct_param", "extraparam")

        test_data = {"data": "data"}
        res = self.dao.update_one("af123", test_data.copy())
        self.assertEquals('PATCH', res.system_data['method'])
        self.assertEquals(self.dao.end_point + '/af123', res.system_data['url'])
        self.assertEquals(test_data, res.message_data)

    def test_get_one_response_different_from_200_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.get_one, "af123")

    def test_get_all_response_different_from_200_204_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.get_all)

    def test_get_all_response_none_when_204(self):

        self.request_adapter.response_status = 204
        self.assertIsNone(self.dao.get_all())

    def test_delete_one_response_different_from_200_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.delete_one, "af123")

    def test_delete_all_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.delete_all)

    def test_update_one_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.update_one, "af123", "message")
