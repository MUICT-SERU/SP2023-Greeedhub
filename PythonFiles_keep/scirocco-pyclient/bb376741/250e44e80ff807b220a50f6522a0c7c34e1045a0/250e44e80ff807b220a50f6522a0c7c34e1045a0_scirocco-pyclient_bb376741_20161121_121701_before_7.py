import unittest

import datetime

from sciroccoclient.exceptions import SciroccoInvalidMessageScheduleTimeError, SciroccoInvalidMessageStatusError
from sciroccoclient.messages import SciroccoMessage


class SciroccoMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = SciroccoMessage()

    def test_node_destination_method_exists(self):
        self.assertTrue("node_destination" in dir(self.message))

    def test_status_method_exists(self):
        self.assertTrue("status" in dir(self.message))

    def test_payload_method_exists(self):
        self.assertTrue("payload" in dir(self.message))

    def test_data_type_method_exists(self):
        self.assertTrue("payload_type" in dir(self.message))

    def test_scheduled_time_method_exists(self):
        self.assertTrue("scheduled_time" in dir(self.message))

    def test_that_all_properties_are_at_initial_state(self):
        message = SciroccoMessage()
        self.assertIsNone(message.node_destination)
        self.assertIsNone(message.payload)
        self.assertIsNone(message.payload_type)
        self.assertIsNone(message.scheduled_time)

    def test_that_setting_scheduled_time_also_sets_scheduled_status(self):
        message = SciroccoMessage()
        message.payload = 'data'
        message.node_destination = 'af123'
        message.scheduled_time = datetime.datetime.utcnow()
        self.assertEqual(message.status, 'scheduled')

    def test_that_pushing_scirocco_message_with_invalid_status_raises_exception(self):
        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'
        message.payload_type = '.extension'
        self.assertRaises(SciroccoInvalidMessageStatusError, setattr, message, 'status', 'This is not a valid status.')

    def test_that_pushing_scirocco_message_with_invalid_scheduled_time_raises_exception(self):
        message = SciroccoMessage()
        message.payload = {"name": "message"}
        message.node_destination = 'af123'
        message.payload_type = '.extension'
        self.assertRaises(SciroccoInvalidMessageScheduleTimeError, setattr, message, 'scheduled_time',
                          'This is not an instance so must raise SciroccoInvalidMessageScheduleTimeError.')
