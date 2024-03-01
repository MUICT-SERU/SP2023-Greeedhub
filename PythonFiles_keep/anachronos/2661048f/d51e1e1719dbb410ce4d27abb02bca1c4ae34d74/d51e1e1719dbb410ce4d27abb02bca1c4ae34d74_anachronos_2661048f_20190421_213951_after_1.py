from datetime import datetime
from queue import Queue
from typing import List

from anachronos.exceptions import AnachronosException
from anachronos.message import Message


class _Anachronos(object):

    def store(self, item):
        raise NotImplementedError


class MessageQueue(_Anachronos):

    def __init__(self):
        self.messages = Queue()
        self.frozen_messages = None

    def store(self, item):
        if self.frozen_messages is not None:
            raise AnachronosException("Anachronos object is frozen. Messages can no longer be stored.")
        self.messages.put(Message(datetime.now(), item))

    def get_messages(self) -> List[Message]:
        if self.frozen_messages is None:
            self.frozen_messages = list(self.messages.queue)

        return self.frozen_messages

    def _reset(self):
        self.messages = Queue()
        self.frozen_messages = None

