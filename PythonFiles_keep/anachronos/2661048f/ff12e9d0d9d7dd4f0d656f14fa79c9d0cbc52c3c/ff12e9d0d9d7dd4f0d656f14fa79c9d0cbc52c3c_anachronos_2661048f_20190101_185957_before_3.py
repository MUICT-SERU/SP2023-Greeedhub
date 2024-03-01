import logging
import multiprocessing
import threading
import time
from typing import Type, Dict, List

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.communication.message_queue_consumer import MessageQueueConsumer
from anachronos.compat.jivago_streams import Stream
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
        self.application_runner.run_app()
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

        return TestReportIndex(Stream(assertion_runners).map(
            lambda assertion_runner: assertion_runner.evaluate(self.anachronos_message_queue)).toList())


test_classes: Dict[Type["TestCase"], Type[ApplicationRunner]] = {}
default_runner = None


def set_default_runner(runner: Type[ApplicationRunner]):
    global default_runner
    default_runner = runner


def _register(runner_class, test_class):
    if runner_class is None and test_classes.get(test_class) is not None:
        return test_class
    test_classes[test_class] = runner_class
    return test_class


def RunWith(runner: Type[ApplicationRunner]):
    return lambda x: _register(runner, x)


def RestartApp(x):
    x.restart_before_running = True
    return x


def run_tests():
    Stream(TestCase.__subclasses__()).forEach(lambda clazz: _register(None, clazz))
    distinct_runner_classes = Stream(test_classes.values()).toSet()
    for runner_class in distinct_runner_classes:

        test_classes_for_runner = Stream(test_classes.items()) \
            .filter(lambda _, runner: runner == runner_class) \
            .map(lambda test_class, _: test_class) \
            .toList()

        if runner_class is None:
            runner_class = default_runner

        report = TestRunner(runner_class, test_classes_for_runner).run()

        Stream(report.subreports).forEach(StdoutReportFormatter().format)
