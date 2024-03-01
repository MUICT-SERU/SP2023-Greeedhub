from typing import List

from anachronos.compat.jivago_streams import Stream
from anachronos.test.reporting.test_report import TestReport


class TestReportIndex(object):

    def __init__(self, subreports: List[TestReport]):
        self.subreports = subreports

    def is_success(self) -> bool:
        return Stream(self.subreports).allMatch(TestReport.is_success)
