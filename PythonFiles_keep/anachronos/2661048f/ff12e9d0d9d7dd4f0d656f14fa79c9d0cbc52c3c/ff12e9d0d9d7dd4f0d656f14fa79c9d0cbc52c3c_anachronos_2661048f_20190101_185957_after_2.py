from typing import Dict, Type

from anachronos.test.boot.application_runner import ApplicationRunner


class AnachronosConfig(object):

    def __init__(self):
        self.test_classes: Dict[Type["TestCase"], Type[ApplicationRunner]] = {}
        self.default_runner: Type[ApplicationRunner] = None

    def set_default_runner(self, runner: Type[ApplicationRunner]):
        self.default_runner = runner

    def get_default_runner(self):
        return self.default_runner

    def register_test_class(self, runner_class, test_class):
        if runner_class is None and self.test_classes.get(test_class) is not None:
            return test_class
        self.test_classes[test_class] = runner_class
        return test_class


anachronos_config = AnachronosConfig()


def DefaultRunner(runner: Type[ApplicationRunner]):
    anachronos_config.set_default_runner(runner)
    return runner


def RunWith(runner: Type[ApplicationRunner]):
    return lambda x: anachronos_config.register_test_class(runner, x)


def RestartApp(x):
    x.restart_before_running = True
    return x
