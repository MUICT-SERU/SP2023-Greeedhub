from typing import List, Dict

from anachronos.communication.logging_interfaces import MessageQueue
from anachronos.exceptions import AnachronosAssertionException
from anachronos.test.assertion import Assertion
from anachronos.test.reporting.test_report import TestReport
from anachronos.test.reporting.test_result import TestResult


class AssertionRunner(object):

    def __init__(self, assertions: Dict[str, List[Assertion]], report_name: str):
        self.report_name = report_name
        self.assertions = assertions

    def evaluate(self, message_queue: MessageQueue) -> TestReport:
        test_results = []
        for test_name, assertions in self.assertions.items():
            error_messages = []
            for assertion in assertions:
                try:
                    assertion.run(message_queue)
                except AnachronosAssertionException as e:
                    error_messages.append(e.message)
                except Exception as e:
                    error_messages.append(str(e))

            if error_messages:
                test_results.append(TestResult.failure(test_name, error_messages))
            else:
                test_results.append(TestResult.success(test_name))

        return TestReport(self.report_name, test_results)
