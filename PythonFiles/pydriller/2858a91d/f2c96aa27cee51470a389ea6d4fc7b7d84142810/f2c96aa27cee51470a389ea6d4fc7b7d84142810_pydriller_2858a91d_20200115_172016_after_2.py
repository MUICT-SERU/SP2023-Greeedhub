"""
Module to calculate the following process metrics for a file \
at a given commit:

    * Commit Count: is the number of commits made to a file
    * Active Developers Count: is the number of developers who contributed \
      to the file
    * Distinct Developers Count: is the cumulative number of distinct \
      developers who contributed to the file
    * Normalized Lines Added: are the normalized (by the total number \
      of added lines) added lines in the file
    * Normalized Lines Deleted: are the normalized (by the total number \
      of deleted lines) deleted lines in the file
    * Owner's Contributed Lines: measures the percentage of the lines \
      authored by the highest contributor of a file

Note: All process metrics are release-duration.
See https://ieeexplore.ieee.org/document/6606589 for more info.
"""

from pydriller.metrics.process.commit_count import CommitCount
from pydriller.metrics.process.devs_count import DevsCount
from pydriller.metrics.process.lines_count import NormalizedLinesCount
from pydriller.metrics.process.owner_lines_count import OwnersContributedLines

def commits_count(path_to_repo: str, filepath: str, to_commit: str = None):
    return CommitCount(path_to_repo, filepath, to_commit=to_commit).count()

def devs_count(path_to_repo: str, filepath: str, to_commit: str = None):
    return DevsCount(path_to_repo, filepath, to_commit=to_commit).count()

def norm_lines_count(path_to_repo: str, filepath: str, to_commit: str = None):
    return NormalizedLinesCount(path_to_repo, filepath,
                                to_commit=to_commit).count()

def owner_contributed_lines(path_to_repo: str, filepath: str, to_commit: str = None):
    return OwnersContributedLines(path_to_repo, filepath,
                                to_commit=to_commit).count()
