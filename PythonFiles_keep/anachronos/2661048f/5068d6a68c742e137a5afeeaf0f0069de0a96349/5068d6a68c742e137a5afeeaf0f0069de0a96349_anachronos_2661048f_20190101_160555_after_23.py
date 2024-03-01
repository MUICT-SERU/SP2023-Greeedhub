import unittest
from unittest import mock

from anachronos.exceptions import AnachronosAssertionException
from anachronos.test.assertion import Assertion
from anachronos.test.assertion_runner import AssertionRunner
from anachronos.test.reporting.test_status import TestStatus

REPORT_NAME = "report_name"

ERROR_MESSAGE = "Error message"


class AssertionRunnerTest(unittest.TestCase):

    def setUp(self):
        self.always_error_assertion: Assertion = mock.create_autospec(Assertion)
        self.always_error_assertion.run.side_effect = AnachronosAssertionException(ERROR_MESSAGE)
        self.always_success_assertion: Assertion = mock.create_autospec(Assertion)

    def test_givenNoAssertionError_whenRunning_thenReturnSuccess(self):
        runner = AssertionRunner({'assertion': [self.always_success_assertion]}, REPORT_NAME)

        test_report = runner.evaluate(None)

        self.assertEqual(1, len(test_report.test_results))
        self.assertEqual(TestStatus.SUCCESS, test_report.test_results[0].status)

    def test_givenAssertionError_whenRunning_thenReturnFailureWithAllErrorMessages(self):
        runner = AssertionRunner({'assertion': [self.always_error_assertion, self.always_success_assertion]}, REPORT_NAME)

        test_report = runner.evaluate(None)

        self.assertEqual(1, len(test_report.test_results))
        self.assertEqual(TestStatus.FAILURE, test_report.test_results[0].status)
        self.assertEqual(ERROR_MESSAGE, test_report.test_results[0].messages[0])
