import unittest

import datetime

from sciroccoclient.exceptions import SciroccoInvalidMessageScheduleTimeError, SciroccoInvalidMessageStatusError
from sciroccoclient.messages import SciroccoMessage


class SciroccoMessageTest(unittest.TestCase):
    def setUp(self):
        self.message = SciroccoMessage()

    def test_destination_method_exists(self):
        self.assertTrue("destination" in dir(self.message))

    def test_status_method_exists(self):
        self.assertTrue("status" in dir(self.message))

    def test_data_method_exists(self):
        self.assertTrue("data" in dir(self.message))

    def test_data_type_method_exists(self):
        self.assertTrue("data_type" in dir(self.message))

    def test_scheduled_time_method_exists(self):
        self.assertTrue("scheduled_time" in dir(self.message))

    def test_that_all_properties_are_at_initial_state(self):
        message = SciroccoMessage()
        self.assertIsNone(message.destination)
        self.assertIsNone(message.data)
        self.assertIsNone(message.data_type)
        self.assertIsNone(message.scheduled_time)

    def test_that_setting_scheduled_time_also_sets_scheduled_status(self):
        message = SciroccoMessage()
        message.data = 'data'
        message.destination = 'af123'
        message.scheduled_time = datetime.datetime.utcnow()
        self.assertEqual(message.status, 'scheduled')

    def test_that_pushing_scirocco_message_with_invalid_status_raises_exception(self):
        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'
        message.data_type = '.extension'
        self.assertRaises(SciroccoInvalidMessageStatusError, setattr, message, 'status', 'This is not a valid status.')

    def test_that_pushing_scirocco_message_with_invalid_scheduled_time_raises_exception(self):
        message = SciroccoMessage()
        message.data = {"name": "message"}
        message.destination = 'af123'
        message.data_type = '.extension'
        self.assertRaises(SciroccoInvalidMessageScheduleTimeError, setattr, message, 'scheduled_time',
                          'This is not an instance so must raise SciroccoInvalidMessageScheduleTimeError.')
