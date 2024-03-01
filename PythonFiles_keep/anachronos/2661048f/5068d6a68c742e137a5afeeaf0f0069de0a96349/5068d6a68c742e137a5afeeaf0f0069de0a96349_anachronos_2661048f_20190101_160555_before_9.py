import inspect
import logging
import multiprocessing
import threading
import time
from typing import Type, Dict

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.communication.message_queue_consumer import MessageQueueConsumer
from anachronos.compat.jivago_streams import Stream
from anachronos.exceptions import AnachronosException
from anachronos.test.boot.application_runner import ApplicationRunner
from anachronos.test.registering_assertion_fixture import AssertionRegistry

LOGGER = logging.getLogger("Anachronos").getChild("TestRunner")


class TestRunner(object):

    def __init__(self, application_runner_class: Type[ApplicationRunner], test_class: Type["TestCase"]):
        self.test_class = test_class
        self.queue = multiprocessing.Queue()
        self.application_runner = application_runner_class(self.queue)
        self.anachronos_message_queue = MessageQueue()
        self.consumer = MessageQueueConsumer(self.queue, self.anachronos_message_queue)

    def run(self):
        self.application_runner.run_app()
        time.sleep(2)
        consumer_thread = threading.Thread(target=self.consumer.listen)
        consumer_thread.start()

        test_fixture = self.test_class()
        test_fixture.setUpClass()

        for name, test_method in inspect.getmembers(test_fixture,
                                                    lambda x: inspect.ismethod(x) and x.__name__.startswith("test")):
            try:
                assertion_registry = AssertionRegistry()
                test_fixture.assertThat = lambda x: assertion_registry.create_fixture()(x)
                test_method()
                # TODO move assertion running?
                time.sleep(1)
                Stream(assertion_registry.assertions).forEach(
                    lambda assertion: assertion.run(self.anachronos_message_queue))

                print(f"{name}: OK")
            except AnachronosException as e:
                print(f"{name}: Failed")
                print(e)
            except Exception as e:
                print(f"{name}: Error")
                print(e)
                continue

        time.sleep(2)
        print("Stopping ApplicationRunner...")
        self.consumer.stop()
        self.application_runner.stop()


test_classes: Dict[Type["TestCase"], Type[ApplicationRunner]] = {}
default_runner = None


def set_default_runner(runner: Type[ApplicationRunner]):
    global default_runner
    default_runner = runner


def _register(runner_class, test_class):
    if runner_class is None and test_classes[test_class] is not None:
        return test_class
    test_classes[test_class] = runner_class
    return test_class


def RunWith(runner: Type[ApplicationRunner]):
    return lambda x: _register(runner, x)


def run_tests():
    for test_class, runner_class in test_classes.items():
        if runner_class is None:
            runner_class = default_runner
        print(f"Running {test_class} with {runner_class}.")
        TestRunner(runner_class, test_class).run()
