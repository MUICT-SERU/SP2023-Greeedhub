from anachronos.test.formatting.report_formatter import ReportFormatter
from anachronos.test.reporting.test_report import TestReport
from anachronos.test.reporting.test_status import TestStatus


class StdoutReportFormatter(ReportFormatter):

    def format(self, report: TestReport):
        print(f"======== TestReport ========")
        print(f"{report.test_report_name}\n")

        for test_result in report.test_results:
            if test_result.is_success():
                print(f"{test_result.test_name}: OK.")
            else:
                print(f"{test_result.test_name}: {self.status_string(test_result.status)}...")
                for message in test_result.messages:
                    print(f"    {message}")

        print(f"============================")

        print(self.status_string(report.status))

    def status_string(self, status: TestStatus) -> str:
        return {TestStatus.SUCCESS: 'All tests have passed.',
                TestStatus.FAILURE: 'There were test failures.',
                TestStatus.ERROR: 'There were unexpected test errors.'}[status]
