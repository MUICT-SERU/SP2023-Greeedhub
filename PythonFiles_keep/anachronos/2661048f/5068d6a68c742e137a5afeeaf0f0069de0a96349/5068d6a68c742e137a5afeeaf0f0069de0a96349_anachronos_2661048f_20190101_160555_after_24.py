import unittest

from anachronos.test.reporting.test_report import TestReport
from anachronos.test.reporting.test_result import TestResult
from anachronos.test.reporting.test_status import TestStatus


class TestReportTest(unittest.TestCase):

    def test_givenAllSuccesses_thenReportStatusIsSuccess(self):
        report = TestReport("", [])

        self.assertEqual(TestStatus.SUCCESS, report.status)

    def test_givenErrorAndFailure_thenReportStatusIsError(self):
        report = TestReport("", [TestResult(TestStatus.FAILURE, "", []), TestResult(TestStatus.ERROR, "", [])])

        self.assertEqual(TestStatus.ERROR, report.status)

    def test_givenFailure_thenReportStatusIsFailure(self):
        report = TestReport("", [TestResult(TestStatus.SUCCESS, "", []), TestResult(TestStatus.FAILURE, "", [])])

        self.assertEqual(TestStatus.FAILURE, report.status)
