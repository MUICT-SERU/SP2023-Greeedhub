from typing import List

from anachronos.test.reporting.test_status import TestStatus


class TestResult(object):

    def __init__(self, status: TestStatus, test_name: str, messages: List[str]):
        self.messages = messages
        self.test_name = test_name
        self.status = status

    def is_success(self) -> bool:
        return self.status == TestStatus.SUCCESS

    @staticmethod
    def success(test_name: str) -> "TestResult":
        return TestResult(TestStatus.SUCCESS, test_name, [])

    @staticmethod
    def failure(test_name: str, messages: List[str]) -> "TestResult":
        return TestResult(TestStatus.FAILURE, test_name, messages)

    @staticmethod
    def error(test_name: str, messages: List[str]) -> "TestResult":
        return TestResult(TestStatus.ERROR, test_name, messages)
