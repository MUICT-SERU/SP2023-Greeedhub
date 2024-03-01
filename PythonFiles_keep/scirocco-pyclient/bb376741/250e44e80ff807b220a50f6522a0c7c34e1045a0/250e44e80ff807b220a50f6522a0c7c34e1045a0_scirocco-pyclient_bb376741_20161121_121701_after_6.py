import datetime
import unittest

from sciroccoclient.exceptions import SciroccoHTTPDAOError
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.messages import SciroccoMessage
from sciroccoclient.metadata import MetaData, MetaDataDescriptor
from test.unit.mocks import RequestAdapterMock


class MessageQueueDAOTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        self.metadata_descriptor = MetaDataDescriptor(MetaData())

        self.dao = MessageQueueDAO(self.request_adapter, self.metadata_descriptor)

    def test_end_point(self):
        self.assertEqual(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, "extraparam")
        res = self.dao.pull()
        self.assertEqual(res.metadata['url'], '/messageQueue')
        self.assertEqual(res.metadata['method'], 'GET')

    def test_push_method_exists(self):
        self.assertTrue("push" in dir(self.dao))

    def test_push_method_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.dao.push, SciroccoMessage(), "sdsdssd")


    def test_push_without_special_fields(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'

        res = self.dao.push(message)
        self.assertTrue(isinstance(res.payload, dict))
        self.assertDictEqual(res.payload, message.payload)
        self.assertEqual(res.metadata['method'], 'POST')
        self.assertEqual(res.metadata['url'], '/messageQueue')

    def test_push_emits_data_type_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'
        message.payload_type = '.extension'
        res = self.dao.push(message)
        self.assertEqual(res.metadata[self.metadata_descriptor.get_http_header_by_field_name('payload_type')], '.extension')

    def test_push_emits_to_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'
        res = self.dao.push(message)
        self.assertEqual(res.metadata[self.metadata_descriptor.get_http_header_by_field_name('node_destination')], 'af123')

    def test_push_emits_scheduled_time_and_status_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'
        message.payload_type = '.extension'
        time = datetime.datetime.now()
        message.scheduled_time = time

        res = self.dao.push(message)
        self.assertEqual(res.metadata[self.metadata_descriptor.get_http_header_by_field_name('scheduled_time')], time.isoformat())
        self.assertEqual(res.metadata[self.metadata_descriptor.get_http_header_by_field_name('status')], 'scheduled')

    def test_push_emits_status_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'

        res = self.dao.push(message)
        self.assertEqual(res.metadata[self.metadata_descriptor.get_http_header_by_field_name('status')], 'pending')


    def test_push_response_different_from_201_raises_dao_error(self):
        self.request_adapter.response_status = 400
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message.payload = {"name": "message"}
        self.assertRaises(SciroccoHTTPDAOError, self.dao.push, message)

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEqual(res.metadata['method'], 'PATCH')
        self.assertEqual(res.metadata['url'], '/messageQueue/af123/ack')

    def test_ack_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.ack, "af123")

    def test_pull_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.pull)
