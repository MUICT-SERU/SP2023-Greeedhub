from anachronos.test.reporting.test_report import TestReport


class ReportFormatter(object):

    def format(self, report: TestReport):
        raise NotImplementedError
