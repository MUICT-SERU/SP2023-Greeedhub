import unittest
from datetime import datetime
from unittest import mock

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.exceptions import AnachronosAssertionException
from anachronos.message import Message
from anachronos.test.assertions.unary import IsStoredOnlyOnce

STORED_ONCE = "STORED_ONCE"

STORED_TWICE = "STORED_TWICE"


class OccursOnlyOnceAssertionTest(unittest.TestCase):

    def setUp(self):
        self.messages = [Message(datetime.now(), STORED_ONCE),
                         Message(datetime.now(), STORED_TWICE),
                         Message(datetime.now(), STORED_TWICE)]

        self.message_queue: MessageQueue = mock.create_autospec(MessageQueue)
        self.message_queue.get_messages.return_value = self.messages

    def test_storedOnce(self):
        assertion = IsStoredOnlyOnce(STORED_ONCE)

        assertion.run(self.message_queue)

    def test_givenStoredTwice_thenRaiseException(self):
        assertion = IsStoredOnlyOnce(STORED_TWICE)

        with self.assertRaises(AnachronosAssertionException):
            assertion.run(self.message_queue)
