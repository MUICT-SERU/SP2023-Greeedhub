from typing import List

from anachronos.compat.jivago_streams import Stream
from anachronos.test.reporting.test_result import TestResult
from anachronos.test.reporting.test_status import TestStatus


class TestReport(object):

    def __init__(self, test_report_name: str, test_results: List[TestResult]):
        self.test_report_name = test_report_name
        self.test_results = test_results

    @property
    def status(self) -> TestStatus:
        if Stream(self.test_results).allMatch(lambda result: result.status == TestStatus.SUCCESS):
            return TestStatus.SUCCESS

        if TestStatus.ERROR in Stream(self.test_results).map(lambda result: result.status).toSet():
            return TestStatus.ERROR

        return TestStatus.FAILURE

    def is_success(self) -> bool:
        return self.status == TestStatus.SUCCESS
