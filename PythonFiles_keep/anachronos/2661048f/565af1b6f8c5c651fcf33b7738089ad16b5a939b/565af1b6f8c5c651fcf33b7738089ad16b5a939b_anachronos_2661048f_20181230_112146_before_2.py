from datetime import datetime
from queue import Queue
from typing import List

import requests

from anachronos.message import Message


class AnachronosException(BaseException):
    pass


class Anachronos(object):

    def store(self, item):
        raise NotImplementedError


class MessageQueue(Anachronos):

    def __init__(self):
        self.messages = Queue()
        self.frozen_messages = None

    def store(self, item):
        if self.frozen_messages is not None:
            raise AnachronosException("Anachronos object is frozen. Messages can no longer be stored.")
        self.messages.put(Message(datetime.now(), item))

    def _get_messages(self) -> List[Message]:
        if self.frozen_messages is None:
            self.frozen_messages = list(self.messages.queue)

        return self.frozen_messages

    def _reset(self):
        self.messages = Queue()
        self.frozen_messages = None


class RemoteAnachronosProxy(Anachronos):

    def __init__(self, url='localhost:4001/'):
        self.url = url

    def store(self, item):
        requests.post(self.url, data={'payload': item})

