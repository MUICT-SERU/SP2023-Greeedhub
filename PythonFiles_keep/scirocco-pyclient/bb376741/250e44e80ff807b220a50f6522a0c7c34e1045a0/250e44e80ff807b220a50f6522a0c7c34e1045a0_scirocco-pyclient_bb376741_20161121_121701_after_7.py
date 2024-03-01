import unittest

import datetime

from sciroccoclient.exceptions import SciroccoInvalidMessageScheduleTimeError, SciroccoInvalidMessageStatusError, \
    SciroccoInvalidMessageError, SciroccoInvalidMessageDestinationError, SciroccoInvalidMessageDataError
from sciroccoclient.messages import SciroccoMessage, SciroccoMessageValidator


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


class SciroccoMessageValidatorTest(unittest.TestCase):

    def setUp(self):
        self.validator = SciroccoMessageValidator()

    def test_that_check_exists(self):
        self.assertTrue("check" in dir(self.validator))

    def test_that_check_destination_exists(self):
        self.assertTrue("check_node_destination" in dir(self.validator))

    def test_that_check_status_exists(self):
        self.assertTrue("check_status" in dir(self.validator))

    def test_that_check_payload_exists(self):
        self.assertTrue("check_payload" in dir(self.validator))

    def test_check_raises_invalid_message(self):
        message = "tHIS IS AN INCORRECT MESSAGE TYPE"
        self.assertRaises(SciroccoInvalidMessageError, self.validator.check, message)

    def test_check_raises_invalid_node_destination(self):
        message = SciroccoMessage()
        self.assertRaises(SciroccoInvalidMessageDestinationError, self.validator.check, message)

    def test_check_raises_invalid_message_status(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        message._status = 'novalid status'
        self.assertRaises(SciroccoInvalidMessageStatusError, self.validator.check, message)

    def test_check_raises_invalid_payload(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        self.assertRaises(SciroccoInvalidMessageDataError, self.validator.check, message)

    def test_message_is_instance_of_scirocco_message(self):
        message = "This message is a string"
        self.assertFalse(self.validator.check_message(message))

    def test_destination_cannot_be_none(self):
        message = SciroccoMessage()
        message.payload = 'asdas'
        self.assertFalse(self.validator.check_node_destination(message))

    def test_status_cannot_be_none(self):
        message = SciroccoMessage()
        message.payload = 'asdas'
        message._status = None
        self.assertFalse(self.validator.check_status(message))

    def test_status_cannot_be_random(self):
        message = SciroccoMessage()
        message._status = 'asdadasd'
        self.assertFalse(self.validator.check_status(message))

    def test_status_can_be_scheduled(self):
        message = SciroccoMessage()
        message.status = 'scheduled'
        self.assertTrue(self.validator.check_status(message))

    def test_status_can_be_pending(self):
        message = SciroccoMessage()
        message.status = 'pending'
        self.assertTrue(self.validator.check_status(message))

    def test_payload_cannot_be_none(self):
        message = SciroccoMessage()
        message.node_destination = 'af123'
        self.assertFalse(self.validator.check_payload(message))


