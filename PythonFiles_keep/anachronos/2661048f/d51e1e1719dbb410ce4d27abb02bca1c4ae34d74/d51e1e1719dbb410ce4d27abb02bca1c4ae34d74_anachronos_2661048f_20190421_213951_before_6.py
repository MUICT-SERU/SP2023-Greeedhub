from anachronos.compat.jivago_streams import Stream
from anachronos.test.formatting.report_formatter import ReportFormatter
from anachronos.test.reporting.test_report import TestReport
from anachronos.test.reporting.test_report_index import TestReportIndex
from anachronos.test.reporting.test_status import TestStatus


class StdoutReportFormatter(ReportFormatter):

    def format_report_index(self, report_index: TestReportIndex):
        Stream(report_index.subreports).forEach(self.format_report)
        print("All tests have passed." if report_index.is_success() else "There were test failures.")

    def format_report(self, report: TestReport):
        print(f"======== TestReport ========")

        print(f"{report.test_report_name}...{self.status_string(report.status)}\n")

        for test_result in report.test_results:
            if test_result.is_success():
                print(f"{test_result.test_name}: OK.")
            else:
                print(f"{test_result.test_name}: {self.status_string(test_result.status)}...")
                for message in test_result.messages:
                    print(f"    {message}")

        print(f"============================")

    def status_string(self, status: TestStatus) -> str:
        return {TestStatus.SUCCESS: 'OK',
                TestStatus.FAILURE: 'Failure',
                TestStatus.ERROR: 'Error'}[status]
