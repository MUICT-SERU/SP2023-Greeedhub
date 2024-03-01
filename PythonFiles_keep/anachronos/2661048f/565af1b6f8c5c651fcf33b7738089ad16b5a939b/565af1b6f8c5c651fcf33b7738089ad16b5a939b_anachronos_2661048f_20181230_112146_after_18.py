import multiprocessing
import threading
from typing import Type

import time

from anachronos.anachronos import MessageQueue
from anachronos.communication.message_queue_consumer import MessageQueueConsumer
from anachronos.test.boot.application_runner import ApplicationRunner


class TestRunner(object):

    def __init__(self, application_runner_class: Type[ApplicationRunner]):
        self.queue = multiprocessing.Queue()
        self.application_runner = application_runner_class(self.queue)
        self.consumer = MessageQueueConsumer(self.queue, MessageQueue())

    def run(self):
        self.application_runner.run_app()
        consumer_thread = threading.Thread(target=self.consumer.listen)
        consumer_thread.start()

        print("has started running")

        time.sleep(10)
        print("stopping")
        self.consumer.stop()
        self.application_runner.stop()
