"""
This module contains the abstract class to implement process metrics.
"""


class ProcessMetric:
    """
    Abstract class to implement process metrics
    """

    def __init__(self, path_to_repo: str,
                 from_commit: str,
                 to_commit: str):
        """
        :path_to_repo: path to a single repo
        :to_commit: the SHA of the commit to stop counting. If None, the
            analysis starts from the latest commit
        :from_commit: the SHA of the commit to start counting. If None, the
            analysis ends to the first commit
        """
        if not from_commit or not to_commit:
            raise TypeError

        self.path_to_repo = path_to_repo
        self.from_commit = from_commit
        self.to_commit = to_commit

    def count(self):
        """
        Implement the main functionality of the metric
        """
        return 0
