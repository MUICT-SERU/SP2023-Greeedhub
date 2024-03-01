import logging
import multiprocessing
import sys
import threading
import time
from typing import Type, List

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.communication.message_queue_consumer import MessageQueueConsumer
from anachronos.compat.jivago_streams import Stream
from anachronos.configuration import anachronos_config
from anachronos.test.assertion_runner import AssertionRunner
from anachronos.test.boot.application_runner import ApplicationRunner
from anachronos.test.boot.test_case import TestCase
from anachronos.test.boot.test_suite import TestSuite
from anachronos.test.formatting.stdout_report_formatter import StdoutReportFormatter
from anachronos.test.reporting.test_report_index import TestReportIndex

LOGGER = logging.getLogger("Anachronos").getChild("TestRunner")


class TestRunner(object):

    def __init__(self, application_runner_class: Type[ApplicationRunner], test_classes: List[Type["TestCase"]]):
        self.test_classes = test_classes
        self.queue = multiprocessing.Queue()
        self.application_runner = application_runner_class(self.queue)
        self.anachronos_message_queue = MessageQueue()
        self.consumer = MessageQueueConsumer(self.queue, self.anachronos_message_queue)

    def run(self) -> TestReportIndex:
        self.application_runner.run()
        time.sleep(1)
        consumer_thread = threading.Thread(target=self.consumer.listen)
        consumer_thread.start()

        assertion_runners = []
        for test_class in self.test_classes:
            suite = TestSuite(test_class)

            suite.run()
            assertion_runners.append(AssertionRunner(suite.assertions_by_test, test_class.__name__))

        time.sleep(2)
        print("Stopping ApplicationRunner...")
        self.consumer.stop()
        self.application_runner.stop()

        return TestReportIndex(Stream(assertion_runners)
                               .map(lambda assertion_runner: assertion_runner.evaluate(self.anachronos_message_queue))
                               .toList(),
                               self.anachronos_message_queue.get_messages())


def run_tests():
    Stream(TestCase.__subclasses__()).forEach(lambda clazz: anachronos_config.register_test_class(None, clazz))
    distinct_runner_classes = Stream(anachronos_config.test_classes.values()).toSet()
    reports = []
    for runner_class in distinct_runner_classes:

        test_classes_for_runner = Stream(anachronos_config.test_classes.items()) \
            .filter(lambda _, runner: runner == runner_class) \
            .map(lambda test_class, _: test_class) \
            .toList()

        if runner_class is None:
            runner_class = anachronos_config.default_runner

        report_index = TestRunner(runner_class, test_classes_for_runner).run()

        reports.append(report_index)

    Stream(reports).forEach(lambda x: StdoutReportFormatter().format_report_index(x))

    if Stream(reports).allMatch(lambda x: x.is_success()):
        sys.exit(0)
    else:
        sys.exit(1)
