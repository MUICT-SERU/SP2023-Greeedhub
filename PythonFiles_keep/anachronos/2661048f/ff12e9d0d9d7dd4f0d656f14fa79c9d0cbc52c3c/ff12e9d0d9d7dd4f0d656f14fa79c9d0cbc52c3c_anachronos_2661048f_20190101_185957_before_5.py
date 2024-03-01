from typing import List

from anachronos.test.reporting.test_report import TestReport


class TestReportIndex(object):

    def __init__(self, subreports: List[TestReport]):
        self.subreports = subreports
