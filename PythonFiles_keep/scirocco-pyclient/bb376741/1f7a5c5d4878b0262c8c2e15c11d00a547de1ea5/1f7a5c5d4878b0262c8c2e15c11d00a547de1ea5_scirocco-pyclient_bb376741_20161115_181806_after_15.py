import unittest

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.responses import ClientMessageResponse
from sciroccoclient.metadata import MetaDataHydrator
from test.unit.mocks import RequestAdapterMock, RequestAdapterMultipleMessagesMock


class MessageDAOTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        self.dao = MessageDAO(self.request_adapter, MetaDataHydrator())

    def test_end_point(self):
        self.assertEqual('/messages', self.dao.end_point)

    def test_get_one(self):
        self.assertTrue("get_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.get_one)
        self.assertRaises(TypeError, self.dao.get_one, "extraparam", "extraparam")
        res = self.dao.get_one("af123")
        self.assertEqual('GET', res.metadata['method'])
        self.assertEqual(self.dao.end_point + '/af123', res.metadata['url'])

    def test_get_all_exists(self):
        self.assertTrue("get_all" in dir(self.dao))

    def test_get_all_accepts_no_params(self):
        self.assertRaises(TypeError, self.dao.get_all, "extraparam")

    def test_get_all(self):
        dao = MessageDAO(RequestAdapterMultipleMessagesMock(), MetaDataHydrator())
        res = dao.get_all()
        self.assertIsInstance(res, list)
        for r in res:
            self.assertIsInstance(r, ClientMessageResponse)

    def test_get_all_response_different_from_200_204_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.get_all)

    def test_get_all_response_none_when_204(self):

        self.request_adapter.response_status = 204
        self.assertIsNone(self.dao.get_all())

    def test_delete_one(self):
        self.assertTrue("delete_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.delete_one)
        self.assertRaises(TypeError, self.dao.delete_one, "extraparam", "extraparam")

        res = self.dao.delete_one('af123')
        self.assertEqual('DELETE', res.metadata['method'])
        self.assertEqual(self.dao.end_point + '/af123', res.metadata['url'])

    def test_delete_all(self):
        self.assertTrue("delete_all" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.delete_all, "extraparam")

        res = self.dao.delete_all()
        self.assertEqual('DELETE', res.metadata['method'])
        self.assertEqual(self.dao.end_point, res.metadata['url'])

    def test_update_one(self):
        self.assertTrue("update_one" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.update_one)
        self.assertRaises(TypeError, self.dao.update_one, "correct_param", "correct_param", "extraparam")

        test_data = {"data": "data"}
        res = self.dao.update_one("af123", test_data.copy())
        self.assertEqual('PATCH', res.metadata['method'])
        self.assertEqual(self.dao.end_point + '/af123', res.metadata['url'])
        self.assertEqual(test_data, res.payload)

    def test_get_one_response_different_from_200_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.get_one, "af123")



    def test_delete_one_response_different_from_200_raises_dao_error(self):

        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.delete_one, "af123")

    def test_delete_all_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.delete_all)

    def test_update_one_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.update_one, "af123", "message")
