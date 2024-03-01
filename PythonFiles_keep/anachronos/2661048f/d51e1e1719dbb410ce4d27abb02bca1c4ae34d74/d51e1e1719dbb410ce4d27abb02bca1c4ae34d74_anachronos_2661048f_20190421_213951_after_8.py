import unittest
from datetime import datetime, timedelta
from unittest import mock

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.exceptions import AnachronosAssertionException
from anachronos.message import Message
from anachronos.test.assertions.schedule import OccursEveryXSeconds

RELEVANT_MESSAGE = "hello"

START_TIME = datetime.now()


class OccursEveryXSecondsTest(unittest.TestCase):

    def setUp(self):
        self.messages = [Message(START_TIME, RELEVANT_MESSAGE),
                         Message(START_TIME + timedelta(seconds=1), RELEVANT_MESSAGE),
                         Message(START_TIME + timedelta(seconds=2), "foo")]
        self.message_queue: MessageQueue = mock.create_autospec(MessageQueue)
        self.message_queue.get_messages.return_value = self.messages

        self.assertion = OccursEveryXSeconds(RELEVANT_MESSAGE, 1)

    def test_givenMessageEvery1Second_whenRunning_thenDoNotRaiseAssertionException(self):
        self.assertion.run(self.message_queue)

    def test_givenAMessageSkip_whenRunningAssertion_thenRaiseAssertionException(self):
        self.messages.append(Message(START_TIME + timedelta(seconds=10), RELEVANT_MESSAGE))

        with self.assertRaises(AnachronosAssertionException):
            self.assertion.run(self.message_queue)
