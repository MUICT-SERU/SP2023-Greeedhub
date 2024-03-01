import datetime
import unittest

from sciroccoclient.exceptions import SciroccoHTTPDAOError, SciroccoInvalidMessageError, \
    SciroccoInvalidMessageDestinationError
from sciroccoclient.http.messagequeuedao import MessageQueueDAO
from sciroccoclient.messages import SciroccoMessage
from sciroccoclient.systemdata import SystemData, SystemDataDescriptor
from test.unit.mocks import RequestAdapterMock


class MessageQueueDAOTest(unittest.TestCase):
    def setUp(self):
        self.request_adapter = RequestAdapterMock()
        self.system_data_descriptor = SystemDataDescriptor(SystemData())

        self.dao = MessageQueueDAO(self.request_adapter, self.system_data_descriptor)

    def test_end_point(self):
        self.assertEqual(self.dao.end_point, '/messageQueue')

    def test_pull(self):
        self.assertTrue("pull" in dir(self.dao))
        self.assertRaises(TypeError, self.dao.pull, "extraparam")
        res = self.dao.pull()
        self.assertEqual(res.system_data['url'], '/messageQueue')
        self.assertEqual(res.system_data['method'], 'GET')

    def test_push_method_exists(self):
        self.assertTrue("push" in dir(self.dao))

    def test_push_method_only_accepts_one_param(self):
        self.assertRaises(TypeError, self.dao.push, SciroccoMessage(), "sdsdssd")

    def test_push_param_needs_to_be_scirocco_message_instance(self):
        self.assertRaises(SciroccoInvalidMessageError, self.dao.push, "data")

    def test_push_without_special_fields(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'

        res = self.dao.push(message)
        self.assertTrue(isinstance(res.message_data, dict))
        self.assertDictEqual(res.message_data, message.data)
        self.assertEqual(res.system_data['method'], 'POST')
        self.assertEqual(res.system_data['url'], '/messageQueue')

    def test_push_emits_data_type_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'
        message.data_type = '.extension'
        res = self.dao.push(message)
        self.assertEqual(res.system_data[self.system_data_descriptor.get_http_header_by_field_name('data_type')], '.extension')

    def test_push_emits_to_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'
        res = self.dao.push(message)
        self.assertEqual(res.system_data[self.system_data_descriptor.get_http_header_by_field_name('to')], 'af123')

    def test_push_emits_scheduled_time_and_status_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'
        message.data_type = '.extension'
        time = datetime.datetime.now()
        message.scheduled_time = time

        res = self.dao.push(message)
        self.assertEqual(res.system_data[self.system_data_descriptor.get_http_header_by_field_name('scheduled_time')], time.isoformat())
        self.assertEqual(res.system_data[self.system_data_descriptor.get_http_header_by_field_name('status')], 'scheduled')

    def test_push_emits_status_header(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'

        res = self.dao.push(message)
        self.assertEqual(res.system_data[self.system_data_descriptor.get_http_header_by_field_name('status')], 'pending')

    def test_push_that_no_destination_raises_exception(self):
        self.request_adapter.response_status = 201

        message = SciroccoMessage()
        message.data = {"name": "message"}
        self.assertRaises(SciroccoInvalidMessageDestinationError, self.dao.push, message)

    def test_push_response_different_from_201_raises_dao_error(self):
        self.request_adapter.response_status = 400
        message = SciroccoMessage()
        message.destination = 'af123'
        message.data = {"name": "message"}
        self.assertRaises(SciroccoHTTPDAOError, self.dao.push, message)

    def test_ack(self):
        self.assertTrue('ack' in dir(self.dao))
        self.assertRaises(TypeError, self.dao, "param", "extraparam")

        res = self.dao.ack('af123')

        self.assertEqual(res.system_data['method'], 'PATCH')
        self.assertEqual(res.system_data['url'], '/messageQueue/af123/ack')

    def test_ack_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.ack, "af123")

    def test_pull_response_different_from_200_raises_dao_error(self):
        self.request_adapter.response_status = 400
        self.assertRaises(SciroccoHTTPDAOError, self.dao.pull)
