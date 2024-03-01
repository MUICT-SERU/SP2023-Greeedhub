import unittest

from sciroccoclient.client import Client
from sciroccoclient.http.messagedao import MessageDAO
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.metadata import MetaDataDescriptor, MetaData, MetaDataHydrator
from test.unit.mocks import RequestAdapterMock


class ClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request_adapter = RequestAdapterMock()
        metadata_descriptor = MetaDataDescriptor(MetaData())

        cls.client = Client(MessageDAO(cls.request_adapter, MetaDataHydrator()),
                            MessageQueueDAO(cls.request_adapter, metadata_descriptor))

    def test_method_message_get_exists(self):
        self.assertTrue("get" in dir(self.client))

    def test_method_message_get_accepts_only_one_param(self):
        self.assertRaises(TypeError, self.client.get, "3443", "extraparam")

    def test_method_message_get_all_exists(self):
        self.assertTrue("get_all" in dir(self.client))

    def test_method_message_get_all_noparams(self):
        self.assertRaises(TypeError, self.client.get_all, "sd")

    def test_method_message_delete_one_exists(self):
        self.assertTrue("delete_one" in dir(self.client))

    def test_method_message_delete_one_accepts_only_one_param(self):
        self.assertRaises(TypeError, self.client.delete_one, "ssd", "sds")

    def test_method_message_delete_all_exists(self):
        self.assertTrue("delete_all" in dir(self.client))

    def test_method_message_delete_all_noparams(self):
        self.assertRaises(TypeError, self.client.delete_all, "sd")

    def test_method_message_update_one_exists(self):
        self.assertTrue("update_one" in dir(self.client))

    def test_method_message_update_one_accepts_only_two_params(self):
        self.assertRaises(TypeError, self.client.update_one, "sd", "sd", "sd")

    def test_method_mesage_queue_push_exists(self):
        self.assertTrue("push" in dir(self.client))

    def test_method_mesage_queue_pull_exists(self):
        self.assertTrue("pull" in dir(self.client))

    def test_message_queue_pull_not_accepting_params(self):
        self.assertRaises(TypeError, self.client.pull, "sds")

    def test_message_queue_push_accepts_only_four_params(self):
        self.assertRaises(TypeError, self.client.push, "sds", "sd", "sd", "sdd", "aas")

    def test_method_mesage_queue_ack_exists(self):
        self.assertTrue("ack" in dir(self.client))

    def test_mesage_queue_ack_accepts_only_one_params(self):
        self.assertRaises(TypeError, self.client.ack, "sds", "sd")
